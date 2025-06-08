function changeMainImage(imageUrl, variationId, clickedThumb) {
    const mainImage = document.getElementById('main-product-image');
    mainImage.src = imageUrl;
    document.getElementById('selected-variation-id').value = variationId || '';

    // تحديث رابط easyzoom
    const easyzoomLink = mainImage.closest('.easyzoom')?.querySelector('a');
    if (easyzoomLink) {
        easyzoomLink.href = imageUrl;
    }

    // التحكم في تفعيل الثامبنيولز
    document.querySelectorAll('.product-thumb').forEach(thumb => {
        thumb.style.borderColor = 'transparent';
        thumb.classList.remove('active-thumb');
    });
    if (clickedThumb) {
        clickedThumb.style.borderColor = '#007bff';
        clickedThumb.classList.add('active-thumb');
    }

    if (variationId === null && clickedThumb && !clickedThumb.closest('.variation-thumbnails')) {
        document.querySelectorAll('.variations-section li').forEach(li => li.style.borderColor = '#ccc');
    }
}

function handleColorSwatchClick(clickedSwatchElement, imageUrl, variationId) {
    const mainImage = document.getElementById('main-product-image');
    mainImage.src = imageUrl;
    document.getElementById('selected-variation-id').value = variationId || '';

    // تغيير لون الحدود للسواتش المختار
    document.querySelectorAll('.variations-section li').forEach(li => li.style.borderColor = '#ccc');
    if (clickedSwatchElement) {
        clickedSwatchElement.style.borderColor = 'var(--product-title-color, #3498db)';
    }

    // تفعيل الثامبنيولز المرتبطة
    document.querySelectorAll('.product-thumb').forEach(thumb => {
        thumb.style.borderColor = 'transparent';
        thumb.classList.remove('active-thumb');
        if (thumb.src === imageUrl || (thumb.dataset.variationId && thumb.dataset.variationId == variationId)) {
            thumb.style.borderColor = '#007bff';
            thumb.classList.add('active-thumb');
        }
    });

    if (!document.querySelector('.product-thumb.active-thumb') && imageUrl === window.defaultProductImage) {
        const defaultThumb = document.querySelector('.product-thumb[alt*="(default view)"]');
        if (defaultThumb) {
            defaultThumb.style.borderColor = '#007bff';
            defaultThumb.classList.add('active-thumb');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // تعيين الصورة الافتراضية للثامبنيولز
    const defaultThumb = document.querySelector('.product-thumb[alt*="(default view)"]');
    if (defaultThumb) {
        defaultThumb.style.borderColor = '#007bff';
        defaultThumb.classList.add('active-thumb');
    }
});
