/* PawSorb home — pointer drag for .pawsorb-h__rail (touch scrolls natively) */
(function(){
  if (window.__pawsorbHomeRail) return; window.__pawsorbHomeRail = true;
  function bind(rail){
    if (rail.__psBound) return; rail.__psBound = true;
    var down=false,startX=0,startLeft=0,moved=false;
    rail.addEventListener('pointerdown',function(e){ if(e.pointerType!=='mouse'||rail.scrollWidth<=rail.clientWidth) return; down=true;moved=false;startX=e.clientX;startLeft=rail.scrollLeft; });
    window.addEventListener('pointermove',function(e){ if(!down) return; var dx=e.clientX-startX; if(Math.abs(dx)>4){moved=true;rail.classList.add('is-dragging');} rail.scrollLeft=startLeft-dx; });
    window.addEventListener('pointerup',function(){ if(!down) return; down=false; rail.classList.remove('is-dragging'); });
    rail.addEventListener('click',function(e){ if(moved){e.preventDefault();e.stopPropagation();moved=false;} },true);
  }
  function init(){ document.querySelectorAll('.pawsorb-h__rail').forEach(bind); }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
  document.addEventListener('shopify:section:load',init);
})();
