"""
OCR Service
Uses Google Gemini AI to extract invoice data from images
"""
import json
import logging
import google.generativeai as genai

from config.settings import settings
from models.invoice import InvoiceData, InvoiceItem

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class OCRService:
    """Service for extracting invoice data using Gemini Vision."""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.prompt = self._build_prompt()
    
    def _build_prompt(self) -> str:
        """Build the extraction prompt."""
        return """
    أنت خبير محترف في قراءة واستخراج بيانات الفواتير المكتوبة بخط اليد والمطبوعة.

    ⚠️ مهم جداً: ركز على قراءة الأرقام بدقة شديدة. تأكد من كل رقم قبل إدخاله.

    قم بتحليل صورة الفاتورة واستخرج البيانات التالية بدقة:

    أرجع البيانات بصيغة JSON فقط بدون أي نص إضافي، بالهيكل التالي:

    {
        "supplier_name": "اسم المورد/الشركة",
        "tax_number": "الرقم الضريبي",
        "invoice_number": "رقم الفاتورة",
        "invoice_date": "تاريخ الفاتورة",
        "items": [
            {
                "name": "اسم الصنف",
                "quantity": 0.0,
                "unit": "الوحدة",
                "unit_price": 0.0,
                "total": 0.0
            }
        ],
        "subtotal": 0.0,
        "discount": 0.0,
        "tax_rate": 0.0,
        "tax_amount": 0.0,
        "total_amount": 0.0
    }

    تعليمات مهمة:
    - ⚠️ **اقرأ الأرقام بعناية فائقة** - تحقق من كل رقم مرتين
    - tax_rate هي نسبة الضريبة (مثلاً 15 تعني 15%)
    - إذا كان الرقم غير واضح، حاول استنتاجه من سياق الفاتورة
    - إذا لم تجد قيمة معينة، اتركها فارغة أو 0
    - الأرقام يجب أن تكون أرقام وليست نصوص
    - تحقق من جمع الأصناف = المجموع الفرعي
    - أرجع JSON فقط بدون أي شرح

    📦 **تعليمات خاصة بالوحدات (مهم جداً):**
    
    1. **إذا كانت الوحدة مدمجة في اسم الصنف:**
       - مثال: "علبة عصير 100 مل جهينة" مع كمية 4
       - الاسم يصبح: "علبة عصير جهينة" (بدون 100 مل)
       - الكمية تصبح: 400 (4 × 100)
       - الوحدة تصبح: "مل"
    
    2. **الوحدات المعروفة:** مل، لتر، جم، كجم، سم، متر، ملل
    
    3. **إذا لم توجد وحدة قياس، استخدم نوع التعبئة:**
       - "كيس شيبسي" → الوحدة: "كيس"
       - "علبة عصير" → الوحدة: "علبة"
       - "باكو بسكوت" → الوحدة: "باكو"
       - "زجاجة مياه" → الوحدة: "زجاجة"
       - "قطعة جبنة" → الوحدة: "قطعة"
       - "عبوة زبادي" → الوحدة: "عبوة"
    """
    
    async def extract_from_image(self, image_bytes: bytes) -> InvoiceData:
        """Extract invoice data from image bytes."""
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
            
            # Generate response
            response = self.model.generate_content([self.prompt, image_part])
            
            # Parse JSON response
            json_str = response.text.strip()
            
            # Remove markdown code blocks if present
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            
            data = json.loads(json_str)
            
            # Convert to InvoiceData
            invoice = InvoiceData(
                supplier_name=data.get("supplier_name", ""),
                tax_number=data.get("tax_number", ""),
                invoice_number=data.get("invoice_number", ""),
                invoice_date=data.get("invoice_date", ""),
                subtotal=float(data.get("subtotal", 0)),
                discount=float(data.get("discount", 0)),
                tax_rate=float(data.get("tax_rate", 0)),
                tax_amount=float(data.get("tax_amount", 0)),
                total_amount=float(data.get("total_amount", 0)),
            )
            
            # Convert items
            for item_data in data.get("items", []):
                item = InvoiceItem(
                    name=item_data.get("name", ""),
                    quantity=float(item_data.get("quantity", 0)),
                    unit=item_data.get("unit", ""),
                    unit_price=float(item_data.get("unit_price", 0)),
                    total=float(item_data.get("total", 0)),
                )
                invoice.items.append(item)
            
            logger.info(f"Successfully extracted invoice: {invoice.invoice_number}")
            return invoice
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return InvoiceData()            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            # Return empty invoice without validation message (will be handled by handler)
            return InvoiceData()

# Global instance
ocr_service = OCRService()