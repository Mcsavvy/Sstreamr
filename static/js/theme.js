darkmode = {
    primary: '#0094F8',
    secondary: '#1469ba8c',
    shadow: '#2d495d',
    background: '#161618',
    root: document.querySelector(':root'),
    set: function(color, abbr){
        this.root.style.setProperty(abbr || `--${color}`, this[color] || 'red')
    },
    load: function(){
        this.set('primary', '--pm')
        this.set('secondary', '--sc')
        this.set('shadow', '--sh')
        this.set('background', '--bg')
        this.set('primary', '--dk-pm')
        this.set('secondary', '--dk-sc')
        this.set('shadow', '--dk-sh')
        this.set('background', '--dk-bg')
        lightmode.unload()
        $('#theme-fab button').html('<i class="fas fa-sun"></i>')
    },
    unload: function(){
        this.set('primary', '--r-pm')
        this.set('secondary', '--r-sc')
        this.set('shadow', '--r-sh')
        this.set('background', '--r-bg')
        this.set('primary', '--dk-pm')
        this.set('secondary', '--dk-sc')
        this.set('shadow', '--dk-sh')
        this.set('background', '--dk-bg')

    }
}

lightmode = {
    primary: '#0094F8',
    secondary: '#1469ba8c',
    shadow: '#dbe7f0',
    background: '#FFFFFF',
    root: document.querySelector(':root'),
    set: function(color, abbr){
        this.root.style.setProperty(abbr || `--${color}`, this[color] || 'red')
    },
    load: function(){
        this.set('primary', '--pm')
        this.set('secondary', '--sc')
        this.set('shadow', '--sh')
        this.set('background', '--bg')
        this.set('primary', '--lt-pm')
        this.set('secondary', '--lt-sc')
        this.set('shadow', '--lt-sh')
        this.set('background', '--lt-bg')
        darkmode.unload()
        $('#theme-fab button').html('<i class="fas fa-moon"></i>')
    },
    unload: function(){
        this.set('primary', '--r-pm')
        this.set('secondary', '--r-sc')
        this.set('shadow', '--r-sh')
        this.set('background', '--r-bg')
        this.set('primary', '--lt-pm')
        this.set('secondary', '--lt-sc')
        this.set('shadow', '--lt-sh')
        this.set('background', '--lt-bg')
    }
}

Theme = {
    // Get preferred mode
    createCookie: function(name, value, days) {
        var expires;
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toGMTString();
        }
        else {
            expires = "";
        }
        document.cookie = name + "=" + value + expires + "; path=/";
    },

    // Read cookie
    readCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Erase cookie
    eraseCookie: function(name) {
        this.createCookie(name, "", -1);
    },
    getMode: function() {
        if (this.readCookie("preferredTheme")) {
            return this.readCookie("preferredTheme");
        } else {
            return "not-set";
        }
    },
    isDark: function(){
      if (this.getMode() in {'light-mode':0, 'not-set':1}){
          return false
      } 
      return true
    },
    setMode: function() {
        mode = this.getMode();
        if (mode == 'not-set' || mode == 'light-mode'){
            lightmode.load()
            this.createCookie("preferredTheme", "light-mode", 365);
        } else if (mode == 'dark-mode'){
            darkmode.load()
        }
    },
    darkMode: function(){
        darkmode.load()
        this.createCookie(
            "preferredTheme",
            "dark-mode", 365
        );
    },
    lightMode: function(){
        lightmode.load()
        this.createCookie(
            "preferredTheme",
            "light-mode",
            365
        );
    },
    toggle: function(){
        if (this.getMode() == 'dark-mode'){
            this.lightMode()
        } else{
            this.darkMode()
        }
    }
}