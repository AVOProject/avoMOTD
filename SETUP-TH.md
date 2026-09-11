# avoMOTD — วิธีทำพื้นหลัง (แบนเนอร์) หน้าเซิร์ฟ

คู่มือทำทีละขั้น สำหรับเอา avoMOTD ไปใส่เซิร์ฟใหม่ ให้ได้ **แบนเนอร์ภาพเต็ม 264×16**
ในหน้า multiplayer + **ไอคอนเซิร์ฟ 64×64**

> ต้องรู้ก่อน: หน้า server list มี **2 บรรทัด** เท่านั้น. avoMOTD ทำได้ 2 โหมด
> - **strip** (default) — ย่อรูปเป็นแถบสี 2px ใช้ได้ทุก client ไม่ต้องพึ่งอะไร
> - **full banner** — 66 หัวสกิน 8×8 เรียงเป็นภาพ 264×16 (client **1.21.9+** เท่านั้น,
>   ต่ำกว่านั้น fallback เป็น strip อัตโนมัติ) ต้อง generate ผ่าน MineSkin ครั้งเดียว

> **ทางลัดบนเครื่องเจ้าของ** — clone อยู่ที่ `E:\code\avo-kit\avoMOTD` แล้ว
>
> ```
> python E:\code\avo-kit\kit.py motd <โฟลเดอร์เซิร์ฟ> --image banner.png
> ```
>
> วาง jar + config + รูปให้ทีเดียว ชี้ไอคอนไปที่ของเดิมของเซิร์ฟ แล้วพิมพ์ขั้นที่เหลือ
> พร้อม path จริง. **ไม่ยิง MineSkin ให้** — ขั้นนั้นกินโควตา ต้องสั่งเอง.
> ข้อ 1–5 ข้างล่างคือสิ่งที่คำสั่งนี้ทำ ถ้าจะทำมือก็ทำตามได้

---

## 1. ลงปลั๊กอิน

```
<server>/plugins/avoMOTD-1.0.0.jar
```
เปิดเซิร์ฟ 1 รอบ → ได้ `plugins/avoMOTD/config.yml`

ไม่ต้องลง ProtocolLib หรืออะไรเพิ่ม (inject ผ่าน Paper NMS ตรง ๆ)
ต้องเป็น **Paper** (หรือ fork ของ Paper) — Spigot เปล่าไม่ได้

---

## 2. เตรียมรูป

| ใช้ทำอะไร | ขนาดที่ควรเตรียม |
|---|---|
| แบนเนอร์ | **2112 × 136 px** (= 264×17 คูณ 8 พอดี · อัตราส่วน 15.5:1) |
| ไอคอน | อะไรก็ได้ที่เป็น**สี่เหลี่ยมจัตุรัส** (จะถูกย่อเป็น 64×64) |

วาง `motd.png` (รูปแบนเนอร์) ไว้ที่ `plugins/avoMOTD/`

**ทำไม 2112×136:** ระบบย่อรูปลงเหลือ 264×17 เสมอ (17 แถว — แถวกลางตกลงไปในช่องว่าง
ระหว่างสองบรรทัด). 2112÷264 = 8 และ 136÷17 = 8 → หารลงตัว ย่อแล้วไม่เบลอ
ขนาดอื่นก็ใช้ได้ แต่ถ้าสัดส่วนไม่ใช่ 15.5:1 **รูปจะถูกบีบ** ตัวหนังสือแบนและเบลอ

**สำคัญ:** 264×16 มันเล็กมาก — ตัวหนังสือเล็ก ๆ จะอ่านไม่ออก
ออกแบบให้อ่านออกที่ความสูง 16px (โลโก้ตัวหนา ๆ สีตัดกันชัด)

### ⚠️ AI สร้างรูป 15.5:1 ไม่ได้ — ทดสอบแล้ว อย่าเสียเวลาลองซ้ำ

| ตัวที่ลอง | ขอ 15.5:1 ได้ |
|---|---|
| Gemini 3.6 Flash | ❌ ปฏิเสธเลย |
| Gemini 3.1 Pro | ❌ ได้ 1.83:1 (มันบอกเองว่าทำไม่ได้) |
| ChatGPT | ❌ ได้รูปอ้วน ~5:1 หลัง trim |

เพดานของ image model อยู่ราว 2.4:1 — **เป็นข้อจำกัดของโมเดล ไม่ใช่ prompt ไม่ดี**
เปลี่ยน prompt หรือเปลี่ยนรุ่นก็ไม่ช่วย

**ทางที่ได้ผล เรียงจากคมสุด:**

1. **ทำเองใน Affinity/Photoshop** — canvas 2112×136 **หน่วย px** (เคยพลาดตั้งเป็น mm
   ได้ 24944×1606) วาง art แล้วลากเต็มความกว้าง (Shift ค้าง) ปล่อยล้นบน-ล่าง
   แล้ว**พิมพ์ชื่อเซิร์ฟใหม่ในนั้น** ตัวสูง ~90px ขอบดำหนา = คมที่สุด
2. **ใช้รูป AI แล้วยอมให้บีบ** — ที่เซิร์ฟตอนนี้ใช้แบบนี้ ดูโอเค แค่ตัวหนังสือแบนนิดหน่อย
3. **crop แทนบีบ** — สัดส่วนถูก แต่เนื้อรูปแนวตั้งหายไป ~65%

**ถ้าจะให้ AI ทำรูป** สั่งแบบนี้ได้ผลดีกว่า (สำหรับเอาไปครอป/วางใน Affinity ต่อ):

```
Pixel art, very wide banner. Hard edges, NO anti-aliasing, NO gradients,
flat colours. Dark night palette. Server name in big bold chunky letters with
a thick black outline. No border, no frame — art fills the canvas edge to edge.
```

รูปโทนมืดดีกว่าสีสด — ช่องว่างกลางแบนเนอร์จะกลืนหายไปกับพื้นมืดได้เนียนกว่า

---

## 3. ไอคอน 64×64

```bash
python tools/make_icon.py <banner.png> <server>/world/icon.png 0.5
```
- เลขท้าย = สัดส่วนความกว้างที่ crop มา (crop จากกลางภาพ)
  **น้อย = ซูมเข้า ตัวใหญ่** / **มาก = ซูมออก เห็นกว้าง** (0.4–0.6 กำลังดี)
- บน-ล่างเติมสีฟ้า/พื้นดินจากแบนเนอร์เอง (letterbox)
- ย่อเป็น 256 สีอัตโนมัติ — **จำเป็น** ดูข้อ 6

ตั้ง path ใน `config.yml`:
```yaml
icon: world/icon.png
```
> path หาไฟล์ 3 ชั้น: absolute → `plugins/avoMOTD/` → **server root**
> ใส่ `world/icon.png` = ไอคอนติดไปกับโลก ย้ายโลกไปไหนก็ตามไป

---

## 4. แบนเนอร์เต็ม (ข้ามได้ถ้าเอาแค่ strip)

**ต้องมี MineSkin API key** (ฟรี): https://account.mineskin.org/keys

> เครื่องเจ้าของเก็บ key ไว้ที่ **`C:\Users\Maru\.mineskin-key`** (นอก git repo ทุกอัน)
> ใช้แบบ `$(cat /c/Users/Maru/.mineskin-key)` อย่า hard-code ลงไฟล์ที่ commit
>
> **MineSkin โชว์ secret ครั้งเดียวตอนสร้าง** อ่านซ้ำไม่ได้ ลืมแล้วต้องสร้างใหม่.
> เคยหายมาแล้วครั้งนึง เพราะไปเก็บไว้ใน `plugins/ImageMOTD/config.yml` แล้วถอด
> ปลั๊กอินนั้นออก โฟลเดอร์หายไปพร้อม key

```bash
python tools/build_banner.py <banner.png> <mineskin-key> <server>/plugins/avoMOTD/banner.json
```
- อัป 66 tiles ขึ้น MineSkin → เขียน `banner.json`
- **ใช้เวลา ~4-5 นาที** (จำกัด 3 วิ/ครั้ง)
- **โควตาฟรี = 100 ครั้ง/ชั่วโมง** → ได้ ~1 แบนเนอร์/ชม.
  ถ้าเต็มโควตา script รอ reset ให้เอง ไม่ต้องทำอะไร
- tile ที่ซ้ำ (เคยอัปแล้ว) ใช้ cache ไม่กินโควตา
- **ต้องใส่ path ปลายทางเสมอ** — ป้องกันเขียนผิดเซิร์ฟ

มี `banner.json` = full banner / ลบทิ้ง = กลับไป strip

### เส้นดำผ่ากลางแบนเนอร์ — แก้ด้วย `shadow_color: -1`

client วางสองบรรทัดของ MOTD ห่างกันมากกว่าความสูง sprite ~2px ช่องนั้นเป็น
**พื้นหลังของ server list** ถ้าไม่ทำอะไรจะเห็นเป็น**เส้นดำผ่ากลางภาพ**

**วิธีแก้ — field เดียวที่ root ของ `banner.json`:**

```json
{"text":"","color":"white","shadow_color":-1,"extra":[ ...66 faces... ]}
```

**ทำไมได้ผล:** client วาด**เงา**ของทุก glyph เยื้องลง-ขวา 1px เสมอ ปกติเงาเป็นสีเข้ม
เลยไม่มีใครสังเกต — แต่**เงาของ sprite ก็คือ sprite อีกอัน**. ตั้งเงาเป็นขาวทึบ
(`-1` = `0xFFFFFFFF`) เงาจะเป็นสำเนาสีจริงของแต่ละหน้า เยื้องลง 1px →
**แถวล่างสุดของบรรทัดบน ตกลงไปในช่องว่างพอดี ถมเส้นดำหายไปเอง**
ภาพยังสว่างขึ้นด้วย เพราะทุกหน้าถูกวาด 2 ครั้ง

**ราคาที่จ่าย:** ภาพเบลอนิดหน่อย มีเงาซ้อนเยื้อง 1px ทั่วทั้งภาพ — คุ้มกว่าเส้นดำเยอะ

**อธิบายเรื่องเยื้อง 1px ด้วย** — ถ้าซูมแบนเนอร์เซิร์ฟไหนแล้วเห็นแถวล่างเยื้องขวา
นั่นคือเงา ไม่ใช่ art เขาทำพลาด

> เครดิต: [tgb20/ImageMOTD](https://github.com/tgb20/ImageMOTD) (GPL-3.0) เป็นคนบันทึก
> เทคนิค `-1` shadow ไว้ — `.color(WHITE).shadowColor(ShadowColor.shadowColor(0xFFFFFFFF))`
>
> **ก่อนหน้านี้เคยลองทางที่ผิด:** ไล่มืดแถวที่ติดรอยต่อให้กลืนกับช่องดำ (`fade_seam`)
> แรงพอจะกลบได้ = กินไป 6 จาก 16 แถว กลายเป็นแถบดำหนากว่าเดิม **ถอดออกไปแล้ว**
> อันนี้แก้ที่ต้นเหตุ ไม่ใช่กลบ

**เปลี่ยนค่านี้ไม่ต้องยิง tile ใหม่** — เป็นแค่ field ใน JSON แก้แล้ว reload ได้เลย
ฟรี ไม่กินโควตา

---

## 5. เปิดใช้

```
/avomotd reload        ← อ่าน config + รูป + banner.json ใหม่ (ไม่ต้องรีเซิร์ฟ)
```
ในเกม: หน้า Multiplayer → **Refresh** (client cache MOTD เก่าไว้)

---

## 6. ⚠️ ข้อจำกัดที่จะกัด — status packet 32767 ตัวอักษร

`description` + `favicon` อยู่ใน **string เดียวกัน จำกัด 32767 ตัว**
เกินแล้ว server ยิง packet ไม่ออก → client ขึ้น **"Can't connect to server"**

ที่กินพื้นที่:
| | ประมาณ |
|---|---|
| แบนเนอร์เต็ม 66 tiles | ~17,000 |
| ไอคอน 64×64 (256 สี) | ~6,500 |
| ไอคอน 64×64 (สีเต็ม) | ~16,000 ← **อันตราย** |

**เคยเจอจริง:** ใส่ไอคอนสีเต็ม → 32,687/32,767 เหลือที่ว่าง 80 bytes
`make_icon.py` เลยย่อ 256 สีให้อัตโนมัติ

**เช็คว่าปลอดภัยไหม:**
```bash
python tools/check_status_size.py <host> <port>
```

### เซิร์ฟที่มีไอคอนของตัวเองอยู่แล้ว

**อย่าสร้างทับ** — ชี้ config ไปที่ของเดิมแทน:
```yaml
icon: server-icon.png     # ไอคอนเซิร์ฟมาตรฐาน อยู่ที่ราก server
```
`resolveFile()` หาไล่ 3 ที่: absolute path → `plugins/avoMOTD/` → รากเซิร์ฟ

⚠️ **ระวัง `world/icon.png` ไม่ใช่ไอคอนเซิร์ฟ** — มันคือรูปย่อของ world ที่โผล่ใน
ลิสต์ singleplayer คนละไฟล์กับ `server-icon.png` ทับแล้วรูป world หาย

ไอคอนของเจ้าของมักเป็น PNG สีเต็ม กิน ~16-17k → **บวกกับ banner แล้วเกินเพดาน**
บีบก่อนโดยไม่เปลี่ยนดีไซน์ (สำรองตัวเดิมไว้ก่อนเสมอ):
```bash
cp server-icon.png server-icon-original.png
python -c "from PIL import Image; im=Image.open('server-icon.png').convert('RGB'); \
im.quantize(colors=192).save('server-icon.png', optimize=True)"
```
ของจริงที่วัดได้: 12059 → 4318 bytes (17694 → 5894 chars) ต่างจากตาเปล่า 6.4/255

---

## 7. แจกต่อได้ไหม

**ได้ ไม่มีข้อจำกัด** — `banner.json` เก็บแค่ **URL ถาวรของ textures.minecraft.net**
ไม่มี API key ฝัง, jar ไม่เรียก MineSkin ตอนรัน

แจกแค่นี้พอ:
```
plugins/avoMOTD-1.0.0.jar
plugins/avoMOTD/banner.json     ← generate เสร็จแล้ว
plugins/avoMOTD/config.yml
world/icon.png
```
ใครโหลดไปเปิดก็เห็นแบนเนอร์เดียวกันทันที ไม่ต้องมี key ไม่กินโควตา ไม่จำกัดจำนวนคน

---

## สรุปคำสั่ง (เซิร์ฟใหม่)

```bash
# 1. วาง jar + เปิดเซิร์ฟ 1 รอบ
# 2. วาง banner.png ที่ plugins/avoMOTD/motd.png

python tools/make_icon.py plugins/avoMOTD/motd.png <server>/world/icon.png 0.5
python tools/build_banner.py plugins/avoMOTD/motd.png <key> <server>/plugins/avoMOTD/banner.json

# 3. config.yml → icon: world/icon.png
# 4. /avomotd reload  → ในเกมกด Refresh
# 5. python tools/check_status_size.py <host> <port>   ← เช็คไม่ชนเพดาน
```

---

## อัปเดตทีหลัง — แก้อะไรต้องยิง tile ใหม่ไหม

ตารางนี้คือสิ่งที่ควรดูก่อนแก้อะไรก็ตาม **ครึ่งบนฟรี ครึ่งล่างกินโควตา**

| แก้อะไร | ต้องยิง tile ใหม่ | ทำยังไง |
|---|---|---|
| `shadow_color` | ❌ **ฟรี** | แก้ field ใน `banner.json` → reload |
| `color` ที่ root | ❌ **ฟรี** | เหมือนกัน |
| `config.yml` (icon, width, enabled) | ❌ **ฟรี** | แก้แล้ว reload |
| เปลี่ยนไอคอน | ❌ **ฟรี** | ไม่เกี่ยวกับ banner เลย |
| **เปลี่ยนรูป `motd.png`** | ✅ 66 อัน | รันใหม่ |
| **เปลี่ยนวิธี crop/resize** | ✅ 66 อัน | hash ของทุก tile เปลี่ยน |
| ยิงรูปเดิมซ้ำ | ❌ **ฟรี** | cache จับได้ → `uploaded=0 reused=66` |

**เช็คก่อนยิงจริงว่าจะฟรีไหม** — รันลง path ชั่วคราวก่อน ถ้าขึ้น `uploaded=0` แปลว่าฟรี:
```bash
python tools/build_banner.py <รูป> <key> D:\Temp\test.json
```

### แก้ `banner.json` ตรงๆ (ไม่กินโควตา)

```bash
python -c "import json,shutil; p=r'<server>\plugins\avoMOTD\banner.json'; \
shutil.copy(p,p+'.bak'); d=json.load(open(p,encoding='utf-8')); \
d['shadow_color']=-1; open(p,'w',encoding='utf-8').write(json.dumps(d,separators=(',',':')))"
```
**สำรอง `.bak` ก่อนเสมอ** ย้อนได้ทันทีถ้าออกมาแย่กว่าเดิม

จากนั้น `avomotd reload` → ในเกมกด **Refresh**

---

## 🚫 อย่าไปยุ่งกับไอคอนของเซิร์ฟ

**ถ้าเซิร์ฟมีไอคอนอยู่แล้ว — ห้ามสร้างทับ ห้ามเปลี่ยน** ชี้ config ไปที่ของเดิม:

```yaml
icon: server-icon.png
```

- ไอคอน**ไม่เกี่ยวกับ banner เลย** คนละระบบ เปลี่ยน banner ไม่ต้องแตะไอคอน
- `make_icon.py` มีไว้สำหรับ**เซิร์ฟใหม่ที่ยังไม่มีไอคอน**เท่านั้น
- ⚠️ **`world/icon.png` ไม่ใช่ไอคอนเซิร์ฟ** — มันคือรูปย่อของ world ในลิสต์
  singleplayer **เขียนทับแล้วรูป world หาย** (เคยพลาดมาแล้วกับ gtayl กู้จาก
  `world_backup_pre-trim/icon.png` ได้)

**ข้อยกเว้นเดียวที่ต้องแตะ** — ไอคอนใหญ่เกินจนรวมกับ banner แล้วชนเพดาน 32767
ถึงค่อยบีบสี **แต่ไม่เปลี่ยนดีไซน์ และสำรองตัวเดิมไว้ก่อน** (ดูข้อ 6)

---

## เซิร์ฟที่ลงแล้ว (บันทึกไว้กันลืม)

| เซิร์ฟ | ที่อยู่ | port | ไอคอน | banner |
|---|---|---|---|---|
| **Farm** (avo2) | `E:\code\Plugin_avo\Server\Farm` | 25566* | `world/icon.png` | ✅ 17004 chars |
| **avoMC** (avo1) | `D:\ServerAVO\avoMC` | 25565 | `world/icon.png` | ✅ |
| **gtayl** | `E:\code\ServerMCworke\gtayl` | 25566* | `server-icon.png` (ของเจ้าของ บีบแล้ว) | ✅ |

\* Farm กับ gtayl ใช้ port เดียวกัน เปิดพร้อมกันไม่ได้ — ตัวที่เปิดทีหลังจะแย่ง port

**ยิงคำสั่งเข้าเซิร์ฟที่รันอยู่ ไม่ต้องรีสตาร์ท:**
```bash
python <avoFarmC>/tools/console.py --server "E:/code/ServerMCworke/gtayl" "avomotd reload"
```
ลองผ่าน ServerTap ก่อน ตกไป RCON เอง. ลงปลั๊กอินใหม่บนเซิร์ฟที่รันอยู่ใช้
`plugman load avoMOTD` (ต้องมี PlugManX)
