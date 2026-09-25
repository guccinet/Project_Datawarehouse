# Piwat Data Warehouse & Analytics Platform

[![Architecture](https://img.shields.io/badge/Architecture-Medallion%20Lakehouse-2563eb?style=for-the-badge)](docs/architecture.md)
[![Django](https://img.shields.io/badge/Backend-Django%205.x-059669?style=for-the-badge)](app/)
[![Airflow](https://img.shields.io/badge/Orchestrator-Apache%20Airflow-0284c7?style=for-the-badge)](dags/)
[![Superset](https://img.shields.io/badge/BI%20Dashboard-Apache%20Superset-ea580c?style=for-the-badge)](superset/)
[![PostgreSQL](https://img.shields.io/badge/OLTP%20DB-PostgreSQL%2016-3b82f6?style=for-the-badge)](postgres/)

ระบบคลังข้อมูลและแพลตฟอร์มการวิเคราะห์ธุรกิจค้าปลีกอัจฉริยะ **Piwat DataCommerce OS** — ครอบคลุมระบบบริหารการขายหน้าร้าน, คลังสินค้า, แคมเปญการตลาด, โลจิสติกส์การจัดส่ง พร้อมท่อส่งข้อมูลอัตโนมัติ (Automated Data Pipeline) สู่สถาปัตยกรรม Medallion Lakehouse

---

## 🏗️ สถาปัตยกรรมระบบ (System Architecture)

```text
                     ┌────────────────────────┐
                     │   Nginx Reverse Proxy   │ :80
                     └───────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │ Django App   │        │ Superset BI  │        │ Airflow ETL  │
  │   :8000      │        │   :8088      │        │   :8080      │
  └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
         │                       │                       │
         ▼                       ▼                       ▼
  ┌──────────────┐        ┌──────────────────────────────┐
  │  PostgreSQL  │        │   Medallion Lakehouse Model   │
  │    :5432     │        │    Bronze → Silver → Gold    │
  │ (OLTP Store) │        │     (Analytical Storage)     │
  └──────────────┘        └──────────────────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
                  ┌──────────────┐
                  │ Redis Broker │ :6379
                  └──────────────┘
```

### รายละเอียดเทคโนโลยีที่เลือกใช้ (Technology Stack)

| เลเยอร์ของระบบ | เทคโนโลยีหลัก | บทบาทและหน้าที่การทำงาน |
|---|---|---|
| **Web Storefront & Admin** | Django 5.x + Vanilla CSS | ระบบหน้าร้านค้าออนไลน์, สต็อกสินค้า, การตลาด และติดตามพัสดุ |
| **OLTP Database** | PostgreSQL 16 | จัดเก็บข้อมูลธุรกรรมการซื้อขายแบบ Relational ทันที |
| **ETL Orchestration** | Apache Airflow 2.x | ควบคุมและจัดตารางรัน Pipeline ดึงข้อมูลประจำวัน |
| **Medallion Pipeline** | Python + Iceberg / SQLite | จัดหมวดหมู่เลเยอร์ข้อมูล Bronze (Raw), Silver (Cleaned), Gold (Star Schema) |
| **Business Intelligence** | Apache Superset | แดชบอร์ดมอนิเตอร์และวิเคราะห์ตัวชี้วัดทางธุรกิจ (KPIs) |
| **Message Broker & Cache** | Redis 7 | แคชข้อมูลของ Superset และจัดการคิวงานของ Airflow |
| **Gateway & Proxy** | Nginx | Reverse Proxy กำหนดทิศทางทราฟฟิกแต่ละพอร์ต |
| **Container Orchestration**| Docker Compose | บริหารจัดการ Service ทั้งหมดในรูปแบบ Containers |

---

## 🎯 สถาปัตยกรรมข้อมูล Medallion Data Modeling

```text
PostgreSQL (ระบบหน้าร้าน OLTP)
    │
    ▼ [Airflow DAG Pipeline: piwat_daily_etl]
    │
    ├── 🥉 Bronze Layer    ข้อมูลดิบที่ Extract มาจากต้นทาง (Raw Snapshots)
    ├── 🥈 Silver Layer    ข้อมูลที่ผ่านการ Cleansing, Deduplication และตรวจสอบ Schema
    └── 🥇 Gold Layer      แบบจำลองมิติดาว (Kimball Star Schema) สำหรับการวิเคราะห์
                                │
                                ▼ [เชื่อมต่อกับ Superset Datasets]
                                │
                            📊 แดชบอร์ดสรุปยอดขายและการตัดสินใจทางธุรกิจ
```

---

## 🚀 เริ่มต้นใช้งานอย่างรวดเร็ว (Quick Start)

### ข้อกำหนดเบื้องต้น (Prerequisites)
- Docker Desktop (เวอร์ชัน 24 ขึ้นไป)
- Docker Compose (v2 ขึ้นไป)
- Python 3.11+ (สำหรับรันสคริปต์เสริม)

### 1. คัดลอกโปรเจ็คและการตั้งค่าสภาพแวดล้อม

```bash
git clone https://github.com/guccinet/Project_Datawarehouse.git
cd Project_Datawarehouse
cp .env.example .env
```

> **หมายเหตุ:** กรุณาตรวจสอบหรือปรับเปลี่ยนรหัสผ่านในไฟล์ `.env` ให้สอดคล้องกับสภาพแวดล้อมที่ต้องการใช้งาน

### 2. สตาร์ทเซอร์วิสทั้งหมดด้วย Docker Compose

```bash
docker compose up -d
```

### 3. การเข้าใช้งานเซอร์วิสในระบบ (Default Endpoints)

| บริการ (Service) | URL สำหรับเข้าใช้งาน | ข้อมูลเข้าสู่ระบบ (Credentials) |
|---|---|---|
| **Piwat Web Application** | [http://localhost:8000](http://localhost:8000) | สามารถเข้าใช้งานได้ทันที |
| **Apache Superset (BI)** | [http://localhost:8088](http://localhost:8088) | `admin` / `admin` |
| **Apache Airflow (ETL)** | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` |
| **Nginx Reverse Gateway** | [http://localhost:80](http://localhost:80) | พอร์ตหลักที่รวมเส้นทาง |

### 4. การสั่งรัน Data Pipeline (Airflow Trigger)

1. เปิดเบราว์เซอร์ไปที่ [http://localhost:8080](http://localhost:8080) เข้าสู่ระบบด้วย `admin` / `admin`
2. ค้นหา DAG ชื่อ **`piwat_daily_etl`**
3. ปรับสถานะเป็น **Active (เปิดสวิตช์)** และกดปุ่ม **Trigger DAG** เพื่อเริ่มต้นการประมวลผลข้อมูล

---

## 📁 โครงสร้างโปรเจ็ค (Project Directory Structure)

```text
Project_Datawarehouse/
├── docker-compose.yml          # คอนฟิกการทำงานของทุก Containers
├── .env.example                # แม่แบบตัวแปรสภาพแวดล้อม
├── setup.py                    # สคริปต์ช่วยเตรียมสภาพแวดล้อม
│
├── app/                        # ระบบเว็บแอปพลิเคชัน Django (Piwat Storefront)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── piwat/                  # โมดูลการตั้งค่าหลัก (Settings, URLs, WSGI)
│   ├── sale/                   # โมดูลการขายและสั่งซื้อสินค้า
│   ├── inventory/              # โมดูลสต็อกและคลังสินค้า
│   ├── marketing/              # โมดูลคูปองและระบบสะสมแต้ม Loyalty
│   ├── logistics/              # โมดูลการจัดส่งและติดตามพัสดุ
│   ├── templates/              # หน้าเว็บ HTML UI
│   └── static/css/styles.css   # ระบบ Design System (Sapphire & Mint Theme)
│
├── dags/                       # Airflow DAGs Pipeline
│   └── piwat_etl.py            # แผนการรัน Medallion ETL Pipeline
│
├── postgres/init/              # สคริปต์เริ่มต้นฐานข้อมูล PostgreSQL
│   └── 01_create_databases.sql
│
├── superset/                   # การตั้งค่า Apache Superset
│   └── superset_config.py
│
├── nginx/                      # การตั้งค่า Nginx Reverse Proxy
│   └── nginx.conf
│
├── docs/                       # เอกสารอธิบายเชิงสถาปัตยกรรมและพจนานุกรมข้อมูล
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── lakehouse.md
└── tests/                      # ชุดทดสอบ Unit Tests
```

---

## 📊 โครงสร้าง Gold Layer Star Schema

### ตารางข้อเท็จจริง (Fact Tables)
* **`fact_sales`**: บันทึกข้อมูลยอดขายระดับรายการย่อย (Order Line Grain) ประกอบด้วย `quantity`, `revenue`, `profit`
* **`fact_inventory`**: บันทึกการเคลื่อนไหวสต็อกเข้า-ออก
* **`fact_logistics`**: ข้อมูลประสิทธิภาพการจัดส่งและค่าขนส่ง

### ตารางมิติข้อมูล (Dimension Tables)
* **`dim_date`**: มิติด้านเวลา (วัน, เดือน, ไตรมาส, ปี, วันหยุด)
* **`dim_product`**: มิติข้อมูลสินค้า (SKU, หมวดหมู่, ต้นทุน, ราคาขาย)
* **`dim_customer`**: มิติข้อมูลลูกค้าและระดับชั้นสมาชิกรอยัลตี (Tier)
* **`dim_carrier`**: มิติผู้ให้บริการขนส่งพัสดุ

---

## 🛠️ คำสั่งที่มีประโยชน์ในระหว่างการพัฒนา (Development Cheatsheet)

```bash
# ตรวจสอบสถานะของ Container ทั้งหมด
docker compose ps

# เรียกดู Logs ของระบบแบบเรียลไทม์
docker compose logs -f

# หยุดการทำงานของระบบ
docker compose down

# ล้างข้อมูลและ Volume ทั้งหมดเพื่อเริ่มต้นใหม่
docker compose down -v

# เข้าใช้งาน PostgreSQL Shell โดยตรง
docker exec -it piwat-postgres psql -U piwat -d piwat
```

---

## 👨‍💻 ผู้พัฒนาโครงการ (Developer)

- **นายพิวัฒน์ (Piwat)**
- สาขาวิชาวิทยาการคอมพิวเตอร์ — มหาวิทยาลัยราชภัฏสุราษฎร์ธานี

---

## 📄 ลิขสิทธิ์ (License)

โครงการนี้เผยแพร่ภายใต้ข้อกำหนดของ [MIT License](LICENSE)
