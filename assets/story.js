(function(){
  function el(t,c){var e=document.createElement(t);if(c)e.className=c;return e;}
  function ytId(u){var m=(u||'').match(/(?:youtube\.com\/(?:watch\?v=|shorts\/|embed\/)|youtu\.be\/)([\w-]{11})/);return m?m[1]:'';}
  function parseVideo(u){if(!u)return null;var m;
    if(m=u.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/|embed\/)|youtu\.be\/)([\w-]{11})/))return{kind:'embed',embed:'https://www.youtube.com/embed/'+m[1]+'?autoplay=1&rel=0'};
    if(m=u.match(/vimeo\.com\/(?:video\/)?(\d+)/))return{kind:'embed',embed:'https://player.vimeo.com/video/'+m[1]+'?autoplay=1'};
    return{kind:'file',src:u};}
  var lb=document.getElementById('lightbox');
  function openLb(fig){var slot=document.getElementById('lbSlot');slot.innerHTML='';
    if(fig.dataset.video){var info=parseVideo(fig.dataset.video);
      if(info&&info.kind==='embed'){var f=el('iframe');f.src=info.embed;f.allow='autoplay; fullscreen; encrypted-media';f.allowFullscreen=true;slot.appendChild(f);}
      else{var v=el('video');v.controls=true;v.loop=true;v.autoplay=true;v.playsInline=true;v.setAttribute('playsinline','');if(fig.dataset.poster)v.poster=fig.dataset.poster;var s=el('source');s.src=info?info.src:fig.dataset.video;v.appendChild(s);slot.appendChild(v);}
    }else{var im=fig.querySelector('img');var i=el('img');i.src=im.src;i.alt=im.alt;slot.appendChild(i);}
    var cap=document.getElementById('lbCap');if(cap)cap.textContent=fig.dataset.cap||'';
    if(lb)lb.classList.add('open');}
  function closeLb(){if(lb){lb.classList.remove('open');}var s=document.getElementById('lbSlot');if(s)s.innerHTML='';}
  document.querySelectorAll('.plate').forEach(function(f){
    f.addEventListener('click',function(){openLb(f);});
    f.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openLb(f);}});
  });
  var lc=document.getElementById('lbClose');if(lc)lc.addEventListener('click',closeLb);
  if(lb)lb.addEventListener('click',function(e){if(e.target===lb)closeLb();});
  addEventListener('keydown',function(e){if(e.key==='Escape')closeLb();});
  function fade(img){if(img.dataset.ph)return;img.dataset.ph='1';
    if(img.complete&&img.naturalWidth)img.classList.add('on');
    else{img.addEventListener('load',function(){img.classList.add('on');},{once:true});
         img.addEventListener('error',function(){img.classList.add('on');},{once:true});}}
  document.querySelectorAll('img.ph').forEach(fade);
  setTimeout(function(){document.querySelectorAll('img.ph:not(.on)').forEach(function(i){i.classList.add('on');});},2500);
  var nav=document.getElementById('nav');
  if(nav){var onScroll=function(){nav.classList.toggle('solid',scrollY>innerHeight*0.6);};
    addEventListener('scroll',onScroll,{passive:true});onScroll();}
  var tgl=document.getElementById('navToggle'),links=document.getElementById('navLinks');
  if(tgl&&links)tgl.addEventListener('click',function(){var o=links.classList.toggle('open');
    tgl.setAttribute('aria-expanded',o);tgl.textContent=o?'閉じる ×':'メニュー ＋';});
})();