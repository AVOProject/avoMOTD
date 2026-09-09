/*
 * avoMOTD — PROPRIETARY SOFTWARE. (c) AVOX2. All rights reserved.
 */
package com.avoproject.avomotd;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import io.netty.channel.Channel;
import io.netty.channel.ChannelDuplexHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelPromise;
import io.papermc.paper.network.ChannelInitializeListenerHolder;
import net.kyori.adventure.key.Key;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.protocol.status.ClientboundStatusResponsePacket;
import net.minecraft.network.protocol.status.ServerStatus;
import net.minecraft.resources.RegistryOps;
import org.bukkit.Bukkit;
import org.bukkit.craftbukkit.CraftServer;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * Emits the 1.21.9 "object"/player-face banner into the server-list status
 * response - the one place Adventure and ProtocolLib cannot reach.
 *
 * <p>Paper's {@link ChannelInitializeListenerHolder} lets us add a Netty handler
 * to every connection. On the outbound {@link ClientboundStatusResponsePacket} we
 * rebuild the {@link ServerStatus} with a description parsed from our own raw JSON
 * through Mojang's own {@link ComponentSerialization} codec - which DOES support
 * object components (that is how the client parses them), unlike Adventure's
 * serializer which drops them.
 *
 * <p>This is compiled against the Mojang-mapped Paper server jar, so it is
 * version-specific by nature (the status packet / codec can change between MC
 * versions). It fails safe: any error leaves the original packet untouched.
 */
public final class StatusInjector {

    private static final Key KEY = Key.key("avomotd", "status");

    private final JavaPlugin plugin;
    private volatile String motdJson;   // null = don't override

    public StatusInjector(JavaPlugin plugin) {
        this.plugin = plugin;
    }

    /** The full status "description" JSON to send, or null to leave the MOTD alone. */
    public void setMotdJson(String json) {
        this.motdJson = json;
    }

    public boolean isActive() {
        return motdJson != null;
    }

    public void register() {
        ChannelInitializeListenerHolder.addListener(KEY, this::onChannel);
        plugin.getLogger().info("[avoMOTD] status injector registered (" + KEY + ")");
    }

    public void unregister() {
        try {
            ChannelInitializeListenerHolder.removeListener(KEY);
        } catch (Throwable ignored) {
        }
    }

    private void onChannel(Channel channel) {
        channel.pipeline().addBefore("packet_handler", "avomotd_status", new ChannelDuplexHandler() {
            @Override
            public void write(ChannelHandlerContext ctx, Object msg, ChannelPromise promise) throws Exception {
                Object out = msg;
                try {
                    String json = motdJson;
                    if (json != null && msg instanceof ClientboundStatusResponsePacket packet) {
                        ServerStatus old = packet.status();
                        Component desc = parse(json);
                        ServerStatus rebuilt = new ServerStatus(desc, old.players(), old.version(),
                                old.favicon(), old.enforcesSecureChat());
                        out = new ClientboundStatusResponsePacket(rebuilt);
                    }
                } catch (Throwable t) {
                    plugin.getLogger().warning("[avoMOTD] status inject failed: " + t);
                }
                super.write(ctx, out, promise);
            }
        });
    }

    /** Parse raw JSON into an NMS component via Mojang's registry-aware codec. */
    private Component parse(String json) {
        var registries = ((CraftServer) Bukkit.getServer()).getServer().registryAccess();
        RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, registries);
        JsonElement tree = JsonParser.parseString(json);
        return ComponentSerialization.CODEC.parse(ops, tree).getOrThrow();
    }
}
