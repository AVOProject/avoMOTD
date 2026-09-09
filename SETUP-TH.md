# avoMOTD — วิธีทำพื้นหลัง (แบนเนอร์) หน้าเซิร์ฟ

คู่มือทำทีละขั้น สำหรับเอา avoMOTD ไปใส่เซิร์ฟใหม่ ให้ได้ **แบนเนอร์ภาพเต็ม 264×16**
ในหน้า multiplayer + **ไอคอนเซิร์ฟ 64×64**

> ต้องรู้ก่อน: หน้า server list มี **2 บรรทัด** เท่านั้น. avoMOTD ทำได้ 2 โหมด
> - **strip** (default) — ย่อรูปเป็นแถบสี 2px ใช้ได้ทุก client ไม่ต้องพึ่งอะไร
> - **full banner** — 66 หัวสกิน 8×8 เรียงเป็นภาพ 264×16 (client **1.21.9+** เท่านั้น,
>   ต่ำกว่านั้น fallback เป็น strip อัตโนมัติ) ต้อง generate ผ่าน MineSkin ครั้งเดียว

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
| แบนเนอร์ | ภาพแนวนอนยาว ๆ อัตราส่วน **~16:1** (สุดท้ายถูกย่อเป็น 264×16) |
| ไอคอน | อะไรก็ได้ที่เป็น**สี่เหลี่ยมจัตุรัส** (จะถูกย่อเป็น 64×64) |

วาง `motd.png` (รูปแบนเนอร์) ไว้ที่ `plugins/avoMOTD/`

**สำคัญ:** 264×16 มันเล็กมาก — ตัวหนังสือเล็ก ๆ จะอ่านไม่ออก
ออกแบบให้อ่านออกที่ความสูง 16px (โลโก้ตัวหนา ๆ สีตัดกันชัด)

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
