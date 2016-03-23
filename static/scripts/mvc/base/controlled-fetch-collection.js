define(["libs/underscore","libs/backbone","mvc/base-mvc"],function(a,b,c){"use strict";{var d=b.Collection.extend({fetch:function(a){return a=this._buildFetchOptions(a),b.Collection.prototype.fetch.call(this,a)},_buildFetchOptions:function(b){b=a.clone(b)||{};var c=this;b.remove=b.remove||!1,b.traditional=!0,b.data=b.data||c._buildFetchData(b);var d=this._buildFetchFilters(b);return a.isEmpty(d)||a.extend(b.data,this._fetchFiltersToAjaxData(d)),b},_buildFetchData:function(b){var c={};return this.order&&(c.order=this.order),a.defaults(a.pick(b,this._fetchParams),c)},_fetchParams:["order","limit","offset","view","keys"],_buildFetchFilters:function(b){return a.clone(b.filters||{})},_fetchFiltersToAjaxData:function(b){var c={q:[],qv:[]};return a.each(b,function(a,b){void 0!==a&&""!==a&&(a===!0&&(a="True"),a===!1&&(a="False"),null===a&&(a="None"),c.q.push(b),c.qv.push(a))}),c},order:null,comparators:{update_time:c.buildComparator("update_time",{ascending:!1}),"update_time-asc":c.buildComparator("update_time",{ascending:!0}),create_time:c.buildComparator("create_time",{ascending:!1}),"create_time-asc":c.buildComparator("create_time",{ascending:!0})},setOrder:function(b,c){c=c||{};var d=this,e=d.comparators[b];if(!a.isUndefined(e)&&e!==d.comparator){var f=d.order;return d.order=b,d.comparator=e,d.trigger("changed-order",d.order,f,d),d.sort(c),d}}});d.extend({limitOnFirstFetch:10,limitPerFetch:4,fetchFirst:function(b){return b=b?a.clone(b):{},this.allFetched=!1,this.lastFetched=0,this.fetchMore(a.extend(b,{reset:!0,limit:this.limitOnFirstFetch}))},fetchMore:function(b){console.log("ControlledFetchCollection.fetchMore:",b),b=a.clone(b||{});var c=this;if(console.log("fetchMore, options.reset:",b.reset),!b.reset&&c.allFetched)return console.warn("allFetched"),jQuery.when();b.offset=b.reset?0:c.lastFetched;var d=b.limit=b.limit||c.limitPerFetch||null;return console.log("fetchMore, limit:",d,"offset:",b.offset),c.trigger("fetching-more"),c.fetch(b).always(function(){c.trigger("fetching-more-done")}).done(function(b){var e=a.isArray(b)?b.length:0;c.lastFetched+=e,console.log("fetchMore, lastFetched:",c.lastFetched),(!d||d>e)&&(c.allFetched=!0,c.trigger("all-fetched",c))})}})}return{ControlledFetchCollection:d}});
//# sourceMappingURL=../../../maps/mvc/base/controlled-fetch-collection.js.map