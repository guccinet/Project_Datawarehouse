from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from sale.models import Product, Order, OrderItem, Cart, CartItem
from inventory.models import StockLevel, StockLog
from marketing.models import Coupon, LoyaltyAccount
from logistics.models import Shipment


class Command(BaseCommand):
    help = 'Seeds initial sample catalog and business data for Piwat DataCommerce OS'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚡ Resetting existing catalog and transaction records...'))

        # Clean slate purge
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Shipment.objects.all().delete()
        Order.objects.all().delete()
        StockLog.objects.all().delete()
        StockLevel.objects.all().delete()
        Product.objects.all().delete()
        Coupon.objects.all().delete()
        LoyaltyAccount.objects.all().delete()

        self.stdout.write('🚀 Seeding refreshed product catalog & inventory fixtures...')

        try:
            with transaction.atomic():
                # 1. Product Catalog Definition
                p1 = Product.objects.create(
                    name='Apple MacBook Pro 16" M3 Max (36GB Unified / 1TB SSD)',
                    sku='PWT-MBP16-MAX',
                    description='เวิร์กสเตชันแล็ปท็อปประสิทธิภาพสูงสุด ขับเคลื่อนด้วยชิปประมวลผล Apple M3 Max พร้อมจอภาพ Liquid Retina XDR 120Hz เพื่อการรันโมเดล Data Analytics และงานวิศวกรรมซอฟต์แวร์ขั้นสูง',
                    price=94900.00,
                    cost=77500.00
                )
                p2 = Product.objects.create(
                    name='Dell UltraSharp 34" Curved USB-C Hub Monitor (U3425WE)',
                    sku='PWT-DEL-34C',
                    description='จอโค้งมุมกว้างระดับ UltraWide WQHD เทคโนโลยี IPS Black ให้ภาพคมชัด มิติสีระดับ 98% DCI-P3 พร้อม KVM Switch และสายชาร์จส่งข้อมูล Thunderbolt 4 เส้นเดียวจบ',
                    price=37900.00,
                    cost=28200.00
                )
                p3 = Product.objects.create(
                    name='Keychron Q3 Pro Wireless Custom Mechanical Keyboard',
                    sku='PWT-KC-Q3PRO',
                    description='คีย์บอร์ดกลไกไร้สายแบบ Tenkeyless บอดี้อะลูมิเนียม CNC Full-Metal รองรับโปรแกรม QMK/VIA สวิตช์ Keychron K Pro Mechanical ถอดเปลี่ยนได้อิสระแบบ Hot-swappable',
                    price=7490.00,
                    cost=4800.00
                )
                p4 = Product.objects.create(
                    name='Sony WH-1000XM5 Wireless Noise-Canceling Headphones',
                    sku='PWT-SNY-XM5',
                    description='หูฟังไร้สายระบบตัดเสียงรบกวนอัจฉริยะ Auto NC Optimizer ไดรเวอร์คาร์บอนไฟเบอร์ 30 มม. รองรับ Hi-Res Audio Wireless และแบตเตอรี่ใช้งานต่อเนื่องสูงสุด 30 ชั่วโมง',
                    price=13990.00,
                    cost=9500.00
                )
                p5 = Product.objects.create(
                    name='Logitech MX Master 3S Wireless Performance Mouse',
                    sku='PWT-LOG-MX3S',
                    description='เมาส์ทำงานระดับพรีเมียม เซ็นเซอร์ Darkfield ความแม่นยำสูง 8,000 DPI ปุ่มคลิก Quiet Click ลดเสียง 90% และล้อเลื่อนเหล็ก MagSpeed แม่เหล็กไฟฟ้าหมุนได้ 1,000 บรรทัด/วินาที',
                    price=4190.00,
                    cost=2750.00
                )
                p6 = Product.objects.create(
                    name='Herman Miller Aeron Ergonomic Chair (Onyx Black Edition)',
                    sku='PWT-HM-AERON',
                    description='เก้าอี้เพื่อสุขภาพระดับพรีเมียมอันดับหนึ่ง ออกแบบตามหลักสรีรศาสตร์พร้อมพนักพิงตาข่าย 8Z Pellicle ระบายอากาศยอดเยี่ยม และระบบรองรับกระดูกสันหลัง PostureFit SL',
                    price=54900.00,
                    cost=41000.00
                )

                self.stdout.write(f'  ✓ Created {Product.objects.count()} premium catalog products.')

                # 2. Stock Allocation by Warehouse Zones
                stock_matrix = [
                    (p1, 15, 'Zone-A1', 4),
                    (p2, 10, 'Zone-A2', 3),
                    (p3, 30, 'Zone-B1', 6),
                    (p4, 25, 'Zone-B2', 5),
                    (p5, 45, 'Zone-C1', 10),
                    (p6, 6,  'Zone-D1', 2),
                ]

                for prod, qty, loc, reorder in stock_matrix:
                    StockLevel.objects.create(
                        product=prod,
                        quantity=qty,
                        location=loc,
                        reorder_point=reorder
                    )
                    StockLog.objects.create(
                        product=prod,
                        change_quantity=qty,
                        log_type='inbound',
                        reason='จัดรับสินค้าเข้าคลังเริ่มต้นระบบ (Initial Stock Inbound)'
                    )

                self.stdout.write(f'  ✓ Allocated inventory stock across {len(stock_matrix)} zones.')

                # 3. Campaign Coupons & Promotions
                now = timezone.now()
                coupons = [
                    Coupon(
                        code='WELCOME_PIWAT',
                        discount_type='percentage',
                        value=10.00,
                        min_purchase=1200.00,
                        start_date=now - timedelta(days=3),
                        end_date=now + timedelta(days=90),
                        active=True
                    ),
                    Coupon(
                        code='TECH1000',
                        discount_type='fixed',
                        value=1000.00,
                        min_purchase=10000.00,
                        start_date=now - timedelta(days=3),
                        end_date=now + timedelta(days=45),
                        active=True
                    ),
                    Coupon(
                        code='VIP15',
                        discount_type='percentage',
                        value=15.00,
                        min_purchase=25000.00,
                        start_date=now - timedelta(days=1),
                        end_date=now + timedelta(days=30),
                        active=True
                    ),
                    Coupon(
                        code='EXPRESS500',
                        discount_type='fixed',
                        value=500.00,
                        min_purchase=5000.00,
                        start_date=now - timedelta(days=1),
                        end_date=now + timedelta(days=60),
                        active=True
                    ),
                ]
                Coupon.objects.bulk_create(coupons)
                self.stdout.write(f'  ✓ Generated {len(coupons)} campaign promotional vouchers.')

                # 4. Customer Loyalty Tier Data
                loyalty_members = [
                    LoyaltyAccount(customer_name='กิตติศักดิ์ พัฒนกุล', phone='0898765432', points=680),
                    LoyaltyAccount(customer_name='ธนภัทร สุวรรณเมธา', phone='0819928374', points=1850),
                    LoyaltyAccount(customer_name='ปิยาภา วิเชียรศรี', phone='0863345512', points=340),
                    LoyaltyAccount(customer_name='ศุภวิชญ์ บวรเกียรติ', phone='0854432198', points=2400),
                ]
                LoyaltyAccount.objects.bulk_create(loyalty_members)
                self.stdout.write(f'  ✓ Registered {len(loyalty_members)} loyalty program members.')

            self.stdout.write(self.style.SUCCESS('🎉 Initial business seed data installed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to seed business data: {str(e)}'))
