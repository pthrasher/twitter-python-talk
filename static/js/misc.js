var Counter,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Counter = (function() {

  function Counter() {
    this.perMin = __bind(this.perMin, this);

    this.perSec = __bind(this.perSec, this);

    this.deltaMin = __bind(this.deltaMin, this);

    this.deltaSec = __bind(this.deltaSec, this);

    this.deltaMs = __bind(this.deltaMs, this);

    this.clear = __bind(this.clear, this);

    this.incr = __bind(this.incr, this);

    this.makeSafeKey = __bind(this.makeSafeKey, this);
    this.stats = {};
  }

  Counter.prototype.makeSafeKey = function(key) {
    var _ref, _ref1, _ref2;
    this.stats[key] = (_ref = this.stats[key]) != null ? _ref : {};
    this.stats[key].count = (_ref1 = this.stats[key].count) != null ? _ref1 : 0;
    return this.stats[key].start = (_ref2 = this.stats[key].start) != null ? _ref2 : +new Date();
  };

  Counter.prototype.incr = function(key, val) {
    if (val == null) {
      val = 1;
    }
    this.makeSafeKey(key);
    return this.stats[key].count += val;
  };

  Counter.prototype.clear = function(key) {
    this.makeSafeKey(key);
    this.stats[key].count = 0;
    return this.stats[key].start = +new Date();
  };

  Counter.prototype.deltaMs = function(key) {
    var count, now, start, _ref, _ref1;
    this.makeSafeKey(key);
    now = +new Date();
    count = (_ref = this.stats[key].count) != null ? _ref : 0;
    start = (_ref1 = this.stats[key].start) != null ? _ref1 : now;
    return now - start;
  };

  Counter.prototype.deltaSec = function(key) {
    var ms;
    ms = this.deltaMs(key);
    return ms / 1000;
  };

  Counter.prototype.deltaMin = function(key) {
    var seconds;
    seconds = this.deltaSec(key);
    return seconds / 60;
  };

  Counter.prototype.perSec = function(key) {
    var count, ps, seconds;
    seconds = this.deltaSec(key);
    count = this.stats[key].count;
    ps = 0;
    if (count > 0 && seconds > 0) {
      ps = count / seconds;
    }
    return ps;
  };

  Counter.prototype.perMin = function(key) {
    var count, min, pm;
    min = this.deltaMin(key);
    count = this.stats[key].count;
    pm = 0;
    if (count > 0 && min > 0) {
      pm = count / min;
    }
    return pm;
  };

  return Counter;

})();

// Some global objects
var counter = new Counter(),
    host = window.location.hostname,
    port = 8001,
    socket = io.connect(host, port),
    should_throttle = true;

