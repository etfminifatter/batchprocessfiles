/**
 * 批量文件处理工具网站性能优化脚本
 */

// 图片懒加载处理
document.addEventListener('DOMContentLoaded', function() {
    // 为所有图片添加懒加载属性
    const images = document.querySelectorAll('img:not([loading])');
    images.forEach(img => {
        img.setAttribute('loading', 'lazy');
    });

    // 监听DOM变化，为新加入的图片添加懒加载
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeName === 'IMG' && !node.hasAttribute('loading')) {
                        node.setAttribute('loading', 'lazy');
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// 平滑滚动实现
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// 移动端导航菜单切换
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.querySelector('.mobile-menu');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinks) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('nav-active');
        });
    }
}); 