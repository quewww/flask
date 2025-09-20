// 移动端菜单切换 
document.getElementById('mobileMenuButton').addEventListener('click', function() { 
    document.getElementById('mobileMenu').classList.toggle('active'); 
}); 

// 平滑滚动 
document.querySelectorAll('a[href^="#"]').forEach(anchor => { 
    anchor.addEventListener('click', function(e) { 
        e.preventDefault(); 
        document.querySelector(this.getAttribute('href')).scrollIntoView({ 
            behavior: 'smooth' 
        }); 
        // 如果是移动端菜单中的链接，点击后关闭菜单 
        if (document.getElementById('mobileMenu').classList.contains('active')) { 
            document.getElementById('mobileMenu').classList.remove('active'); 
        } 
    }); 
});