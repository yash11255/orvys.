// Runs before paint: skip the loading screen after the first page of a visit.
try{if(sessionStorage.getItem("ov-seen")){document.documentElement.classList.add("ld-skip")}sessionStorage.setItem("ov-seen","1")}catch(e){}
