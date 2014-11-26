define([],function(){var a=Backbone.View.extend({el_masthead:"#everything",options:null,$background:null,list:[],initialize:function(e){this.options=e;$("body").off();this.setElement($(this._template(e)));$(this.el_masthead).append($(this.el));this.$background=$(this.el).find("#masthead-background");var d=this;$(window).on("beforeunload",function(){var g="";for(key in d.list){if(d.list[key].options.onunload){var f=d.list[key].options.onunload();if(f){g+=f+" "}}}if(g!=""){return g}})},events:{click:"_click",mousedown:function(d){d.preventDefault()}},append:function(d){return this._add(d,true)},prepend:function(d){return this._add(d,false)},highlight:function(e){var d=$(this.el).find("#"+e+"> li");if(d){d.addClass("active")}},_add:function(g,e){var d=$(this.el).find("#"+g.location);if(d){var f=$(g.el);f.addClass("masthead-item");if(e){d.append(f)}else{d.prepend(f)}this.list.push(g)}return null},_click:function(g){var f=$(this.el).find(".popup");if(f){f.hide()}var d=$(g.target).closest(".masthead-item").find(".popup");if($(g.target).hasClass("head")){d.show();this.$background.show()}else{this.$background.hide()}},_template:function(d){var e=d.brand?("/ "+d.brand):"";return'<div><div id="masthead" class="navbar navbar-fixed-top navbar-inverse"><div style="position: relative; right: -50%; float: left;"><div id="navbar" style="display: block; position: relative; right: 50%;"></div></div><div class="navbar-brand"><a href="'+d.logo_url+'"><img border="0" src="'+galaxy_config.root+'static/images/galaxyIcon_noText.png"><span id="brand"> Galaxy '+e+'</span></a></div><div class="quota-meter-container"></div><div id="iconbar" class="iconbar"></div></div><div id="masthead-background" style="display: none; position: absolute; top: 33px; width: 100%; height: 100%; z-index: 1010"></div></div>'}});var b=Backbone.View.extend({options:{id:"",icon:"fa-cog",tooltip:"",with_number:false,onclick:function(){alert("clicked")},onunload:null,visible:true},location:"iconbar",initialize:function(e){if(e){this.options=_.defaults(e,this.options)}this.setElement($(this._template(this.options)));var d=this;$(this.el).find(".icon").tooltip({title:this.options.tooltip,placement:"bottom"}).on("mouseup",d.options.onclick);if(!this.options.visible){this.hide()}},show:function(){$(this.el).css({visibility:"visible"})},hide:function(){$(this.el).css({visibility:"hidden"})},icon:function(d){$(this.el).find(".icon").removeClass(this.options.icon).addClass(d);this.options.icon=d},toggle:function(){$(this.el).addClass("toggle")},untoggle:function(){$(this.el).removeClass("toggle")},number:function(d){$(this.el).find(".number").text(d)},_template:function(e){var d='<div id="'+e.id+'" class="symbol"><div class="icon fa fa-2x '+e.icon+'"></div>';if(e.with_number){d+='<div class="number"></div>'}d+="</div>";return d}});var c=Backbone.View.extend({options:{id:"",title:"",target:"_parent",content:"",type:"url",scratchbook:false,onunload:null,visible:true,disabled:false,title_attribute:""},location:"navbar",$menu:null,events:{"click .head":"_head"},initialize:function(d){if(d){this.options=_.defaults(d,this.options)}if(this.options.content!==undefined&&this.options.content.indexOf("//")===-1){this.options.content=galaxy_config.root+this.options.content}this.setElement($(this._template(this.options)));if(this.options.disabled){$(this.el).find(".root").addClass("disabled");this._attachPopover()}if(!this.options.visible){this.hide()}},show:function(){$(this.el).css({visibility:"visible"})},hide:function(){$(this.el).css({visibility:"hidden"})},add:function(f){var g={title:"Title",content:"",type:"url",target:"_parent",scratchbook:false,divider:false};if(f){g=_.defaults(f,g)}if(g.content&&g.content.indexOf("//")===-1){g.content=galaxy_config.root+g.content}if(!this.$menu){$(this.el).find(".root").append(this._templateMenu());$(this.el).find(".symbol").addClass("caret");this.$menu=$(this.el).find(".popup")}var e=$(this._templateMenuItem(g));this.$menu.append(e);var d=this;e.on("click",function(h){h.preventDefault();if(d.options.target==="_blank"){return true}Galaxy.frame.add(f)});if(g.divider){this.$menu.append($(this._templateDivider()))}},_head:function(d){d.preventDefault();if(this.options.disabled){return}if(!this.$menu){Galaxy.frame.add(this.options)}},_attachPopover:function(){var d=$(this.el).find(".head");d.popover({html:true,content:'Please <a href="'+galaxy_config.root+'/user/login">log in</a> or <a href="'+galaxy_config.root+'/user/create">register</a> to use this feature.',placement:"bottom"}).on("shown.bs.popover",function(){setTimeout(function(){d.popover("hide")},5000)})},_templateMenuItem:function(d){return'<li><a href="'+d.content+'" target="'+d.target+'">'+d.title+"</a></li>"},_templateMenu:function(){return'<ul class="popup dropdown-menu"></ul>'},_templateDivider:function(){return'<li class="divider"></li>'},_template:function(e){var d='<ul id="'+e.id+'" class="nav navbar-nav" border="0" cellspacing="0"><li class="root dropdown" style=""><a class="head dropdown-toggle" data-toggle="dropdown" target="'+e.target+'" href="'+e.content+'" title="'+e.title_attribute+'">'+e.title+'<b class="symbol"></b></a></li></ul>';return d}});return{GalaxyMasthead:a,GalaxyMastheadTab:c,GalaxyMastheadIcon:b}});