# Authentication System - Simple Frontend

## 🎯 **ระบบ Authentication แบบง่ายๆ ใช้งานได้ทันที**

Frontend ที่สร้างด้วย HTML/CSS/JavaScript ธรรมดา ไม่ใช้ Framework ใดๆ เลย

## 📁 **ไฟล์ในระบบ:**

```
auth-simple-frontend/
├── index.html          # หน้า Login
├── dashboard.html      # หน้า Dashboard
├── style.css          # CSS สำหรับ Login
├── dashboard.css      # CSS สำหรับ Dashboard
├── script.js          # JavaScript สำหรับ Login
├── dashboard.js       # JavaScript สำหรับ Dashboard
└── README.md          # ไฟล์นี้
```

## 🚀 **วิธีใช้งาน:**

### **1. เปิดใน Chrome:**
```bash
# เปิดหน้า Login
chrome index.html

# หรือ double-click ที่ไฟล์ index.html
```

### **2. ข้อมูลทดสอบ:**
```
SuperAdmin:
- Email: admin@example.com
- Password: admin123456

Admin1:
- Email: admin1@example.com  
- Password: admin123
```

### **3. การใช้งาน:**
1. เปิด `index.html` ใน Chrome
2. ใส่ข้อมูล Login
3. กดปุ่ม "เข้าสู่ระบบ"
4. ระบบจะพาไปหน้า Dashboard อัตโนมัติ

## ⚙️ **การตั้งค่า Backend:**

ในไฟล์ `script.js` บรรทัดที่ 2:
```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
```

**เปลี่ยน URL ให้ตรงกับ Backend ของคุณ**

## 🎨 **ฟีเจอร์ที่มี:**

### **หน้า Login:**
- ✅ Glass Morphism Design
- ✅ Animated Background
- ✅ Password Toggle (แสดง/ซ่อน)
- ✅ Remember Me
- ✅ Loading Animation
- ✅ Error/Success Messages
- ✅ Responsive Design

### **หน้า Dashboard:**
- ✅ Sidebar Navigation (ตาม Role)
- ✅ Statistics Cards
- ✅ Real-time Clock
- ✅ User Menu
- ✅ Profile Management
- ✅ Change Password
- ✅ Logout Function
- ✅ Mobile Responsive

### **Role-based Navigation:**
- **SuperAdmin:** ดูได้ทุกอย่าง + จัดการ Admin
- **Admin1-3:** จัดการผู้ใช้ + รายงาน
- **User:** โปรไฟล์ + ภาพรวม

## 🔧 **การปรับแต่ง:**

### **เปลี่ยนสี:**
แก้ไขใน `style.css` และ `dashboard.css`:
```css
/* เปลี่ยนสีหลัก */
background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);

/* เปลี่ยนสีปุ่ม */
.login-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}
```

### **เปลี่ยน API URL:**
แก้ไขใน `script.js`:
```javascript
const API_BASE_URL = 'https://your-api-domain.com/api/v1';
```

### **เพิ่มฟีเจอร์:**
แก้ไขใน `dashboard.js` ฟังก์ชัน:
- `loadAdminManagementContent()`
- `loadUserManagementContent()`
- `loadSystemSettingsContent()`
- `loadAuditLogsContent()`

## 📱 **Responsive Design:**

- ✅ **Desktop:** ใช้งานได้เต็มฟีเจอร์
- ✅ **Tablet:** Sidebar ปรับขนาด
- ✅ **Mobile:** Sidebar แบบ Overlay

## 🛡️ **Security Features:**

- ✅ **JWT Token Authentication**
- ✅ **Auto Logout เมื่อ Token หมดอายุ**
- ✅ **Remember Me Function**
- ✅ **Password Validation**
- ✅ **Role-based Access Control**

## 🚀 **Deploy:**

### **วิธีง่าย:**
1. Copy ไฟล์ทั้งหมดไปยัง Web Server
2. เปิด `index.html` ใน Browser
3. เสร็จแล้ว!

### **วิธี Professional:**
1. Upload ไฟล์ไปยัง Web Hosting
2. ตั้งค่า Domain ให้ชี้ไปที่ `index.html`
3. ปรับ `API_BASE_URL` ให้ชี้ไปยัง Production Backend

## ❗ **ข้อกำหนด:**

- ✅ **Chrome Browser** (แนะนำ)
- ✅ **Backend API** ต้องทำงานอยู่
- ✅ **CORS** ต้องเปิดใน Backend
- ✅ **Internet Connection** (สำหรับ Google Fonts)

## 🐛 **การแก้ปัญหา:**

### **ปัญหา: ไม่สามารถ Login ได้**
```
1. ตรวจสอบ Backend ทำงานหรือไม่
2. ตรวจสอบ API_BASE_URL ถูกต้องหรือไม่
3. เปิด Developer Tools (F12) ดู Console Error
4. ตรวจสอบ CORS Settings ใน Backend
```

### **ปัญหา: หน้าเว็บไม่แสดงถูกต้อง**
```
1. ตรวจสอบไฟล์ CSS โหลดหรือไม่
2. ลองรีเฟรชหน้าเว็บ (Ctrl+F5)
3. ตรวจสอบ Console Error
```

### **ปัญหา: Dashboard ไม่แสดงข้อมูล**
```
1. ตรวจสอบ Token ใน localStorage
2. ตรวจสอบ API Response ใน Network Tab
3. ตรวจสอบ User Role ถูกต้องหรือไม่
```

## 📞 **การสนับสนุน:**

หากมีปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ Console Error ใน Browser (F12)
2. ตรวจสอบ Network Tab สำหรับ API Calls
3. ตรวจสอบ Backend Logs

## 🎉 **ข้อดี:**

- ✅ **ใช้งานง่าย** - เปิดไฟล์ HTML ได้เลย
- ✅ **ไม่มี Dependencies** - ไม่ต้อง install อะไร
- ✅ **Deploy ง่าย** - copy ไฟล์เท่านั้น
- ✅ **แก้ไขง่าย** - แค่แก้ HTML/CSS/JS
- ✅ **เร็ว** - โหลดเร็ว ไม่มี Framework overhead
- ✅ **เสถียร** - ไม่มีปัญหา version conflicts

---

**🔐 Authentication System - Simple & Reliable** 🚀

