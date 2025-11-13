;(function(){
  // Robust binding: try immediately, and also on DOMContentLoaded
  function bindMenu(){
    try{
      const toggle = document.getElementById('menuToggle');
      const panel = document.getElementById('menuPanel');
      if (!toggle || !panel){
        // console.debug('menu: elements not present yet');
        return false;
      }

      function openPanel(){
        panel.classList.add('open');
        toggle.setAttribute('aria-expanded','true');
        panel.setAttribute('aria-hidden','false');
        // fallback visible style
        panel.style.display = 'flex';
      }
      function closePanel(){
        panel.classList.remove('open');
        toggle.setAttribute('aria-expanded','false');
        panel.setAttribute('aria-hidden','true');
        // keep visible none only when closed
        panel.style.opacity = '';
      }

      const doToggle = function(e){
        e && e.preventDefault && e.preventDefault();
        if (panel.classList.contains('open')) closePanel(); else openPanel();
      };

      // remove previous listeners if any
      toggle.replaceWith(toggle.cloneNode(true));
      const newToggle = document.getElementById('menuToggle');
      newToggle.addEventListener('click', doToggle);
      newToggle.addEventListener('pointerdown', function(ev){ ev.preventDefault(); doToggle(ev); });

      // expose helper for inline fallback
      window.toggleMenu = doToggle;

      // click outside closes
      document.addEventListener('click', function(ev){
        if (!panel.classList.contains('open')) return;
        if (newToggle.contains(ev.target) || panel.contains(ev.target)) return;
        closePanel();
      });

      // close on Escape
      document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') closePanel(); });

      // console.info('menu: bound');
      return true;
    }catch(err){
      console.error('menu bind error', err);
      return false;
    }
  }

  if (!bindMenu()){
    document.addEventListener('DOMContentLoaded', function(){ bindMenu(); });
  }
})();
