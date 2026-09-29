/**
 * Task Manager Custom Sidebar Panel for Home Assistant
 *
 * Features:
 * - Tasks & Chores Management (Due date, priority P1-P4, recurring cadences)
 * - Subtasks with smart automatic reset on recurring chore completion
 * - Assignee rotation (Round-Robin, Least Completed, Random)
 * - Gamification (Points, streaks, leaderboards, achievement badges, confetti)
 * - "Things" tracking (appliances, filters, meters, counters with auto-tasks)
 * - Calendar view
 * - Mount / Tablet Kiosk mode with large touch targets and quick user switcher
 * - Full Administration: Users, Labels, Things, Preferences, Backup & Restore
 */

(function () {
  // Standalone QR Code SVG generator
  const QRCodeGen = (function () {
/*! qrcode-svg v1.1.0 | https://github.com/papnkukn/qrcode-svg | MIT license */
function QR8bitByte(t){this.mode=QRMode.MODE_8BIT_BYTE,this.data=t,this.parsedData=[];for(var e=0,r=this.data.length;e<r;e++){var o=[],n=this.data.charCodeAt(e);n>65536?(o[0]=240|(1835008&n)>>>18,o[1]=128|(258048&n)>>>12,o[2]=128|(4032&n)>>>6,o[3]=128|63&n):n>2048?(o[0]=224|(61440&n)>>>12,o[1]=128|(4032&n)>>>6,o[2]=128|63&n):n>128?(o[0]=192|(1984&n)>>>6,o[1]=128|63&n):o[0]=n,this.parsedData.push(o)}this.parsedData=Array.prototype.concat.apply([],this.parsedData),this.parsedData.length!=this.data.length&&(this.parsedData.unshift(191),this.parsedData.unshift(187),this.parsedData.unshift(239))}function QRCodeModel(t,e){this.typeNumber=t,this.errorCorrectLevel=e,this.modules=null,this.moduleCount=0,this.dataCache=null,this.dataList=[]}QR8bitByte.prototype={getLength:function(t){return this.parsedData.length},write:function(t){for(var e=0,r=this.parsedData.length;e<r;e++)t.put(this.parsedData[e],8)}},QRCodeModel.prototype={addData:function(t){var e=new QR8bitByte(t);this.dataList.push(e),this.dataCache=null},isDark:function(t,e){if(t<0||this.moduleCount<=t||e<0||this.moduleCount<=e)throw new Error(t+","+e);return this.modules[t][e]},getModuleCount:function(){return this.moduleCount},make:function(){this.makeImpl(!1,this.getBestMaskPattern())},makeImpl:function(t,e){this.moduleCount=4*this.typeNumber+17,this.modules=new Array(this.moduleCount);for(var r=0;r<this.moduleCount;r++){this.modules[r]=new Array(this.moduleCount);for(var o=0;o<this.moduleCount;o++)this.modules[r][o]=null}this.setupPositionProbePattern(0,0),this.setupPositionProbePattern(this.moduleCount-7,0),this.setupPositionProbePattern(0,this.moduleCount-7),this.setupPositionAdjustPattern(),this.setupTimingPattern(),this.setupTypeInfo(t,e),this.typeNumber>=7&&this.setupTypeNumber(t),null==this.dataCache&&(this.dataCache=QRCodeModel.createData(this.typeNumber,this.errorCorrectLevel,this.dataList)),this.mapData(this.dataCache,e)},setupPositionProbePattern:function(t,e){for(var r=-1;r<=7;r++)if(!(t+r<=-1||this.moduleCount<=t+r))for(var o=-1;o<=7;o++)e+o<=-1||this.moduleCount<=e+o||(this.modules[t+r][e+o]=0<=r&&r<=6&&(0==o||6==o)||0<=o&&o<=6&&(0==r||6==r)||2<=r&&r<=4&&2<=o&&o<=4)},getBestMaskPattern:function(){for(var t=0,e=0,r=0;r<8;r++){this.makeImpl(!0,r);var o=QRUtil.getLostPoint(this);(0==r||t>o)&&(t=o,e=r)}return e},createMovieClip:function(t,e,r){var o=t.createEmptyMovieClip(e,r);this.make();for(var n=0;n<this.modules.length;n++)for(var i=1*n,a=0;a<this.modules[n].length;a++){var s=1*a;this.modules[n][a]&&(o.beginFill(0,100),o.moveTo(s,i),o.lineTo(s+1,i),o.lineTo(s+1,i+1),o.lineTo(s,i+1),o.endFill())}return o},setupTimingPattern:function(){for(var t=8;t<this.moduleCount-8;t++)null==this.modules[t][6]&&(this.modules[t][6]=t%2==0);for(var e=8;e<this.moduleCount-8;e++)null==this.modules[6][e]&&(this.modules[6][e]=e%2==0)},setupPositionAdjustPattern:function(){for(var t=QRUtil.getPatternPosition(this.typeNumber),e=0;e<t.length;e++)for(var r=0;r<t.length;r++){var o=t[e],n=t[r];if(null==this.modules[o][n])for(var i=-2;i<=2;i++)for(var a=-2;a<=2;a++)this.modules[o+i][n+a]=-2==i||2==i||-2==a||2==a||0==i&&0==a}},setupTypeNumber:function(t){for(var e=QRUtil.getBCHTypeNumber(this.typeNumber),r=0;r<18;r++){var o=!t&&1==(e>>r&1);this.modules[Math.floor(r/3)][r%3+this.moduleCount-8-3]=o}for(r=0;r<18;r++){o=!t&&1==(e>>r&1);this.modules[r%3+this.moduleCount-8-3][Math.floor(r/3)]=o}},setupTypeInfo:function(t,e){for(var r=this.errorCorrectLevel<<3|e,o=QRUtil.getBCHTypeInfo(r),n=0;n<15;n++){var i=!t&&1==(o>>n&1);n<6?this.modules[n][8]=i:n<8?this.modules[n+1][8]=i:this.modules[this.moduleCount-15+n][8]=i}for(n=0;n<15;n++){i=!t&&1==(o>>n&1);n<8?this.modules[8][this.moduleCount-n-1]=i:n<9?this.modules[8][15-n-1+1]=i:this.modules[8][15-n-1]=i}this.modules[this.moduleCount-8][8]=!t},mapData:function(t,e){for(var r=-1,o=this.moduleCount-1,n=7,i=0,a=this.moduleCount-1;a>0;a-=2)for(6==a&&a--;;){for(var s=0;s<2;s++)if(null==this.modules[o][a-s]){var h=!1;i<t.length&&(h=1==(t[i]>>>n&1)),QRUtil.getMask(e,o,a-s)&&(h=!h),this.modules[o][a-s]=h,-1==--n&&(i++,n=7)}if((o+=r)<0||this.moduleCount<=o){o-=r,r=-r;break}}}},QRCodeModel.PAD0=236,QRCodeModel.PAD1=17,QRCodeModel.createData=function(t,e,r){for(var o=QRRSBlock.getRSBlocks(t,e),n=new QRBitBuffer,i=0;i<r.length;i++){var a=r[i];n.put(a.mode,4),n.put(a.getLength(),QRUtil.getLengthInBits(a.mode,t)),a.write(n)}var s=0;for(i=0;i<o.length;i++)s+=o[i].dataCount;if(n.getLengthInBits()>8*s)throw new Error("code length overflow. ("+n.getLengthInBits()+">"+8*s+")");for(n.getLengthInBits()+4<=8*s&&n.put(0,4);n.getLengthInBits()%8!=0;)n.putBit(!1);for(;!(n.getLengthInBits()>=8*s||(n.put(QRCodeModel.PAD0,8),n.getLengthInBits()>=8*s));)n.put(QRCodeModel.PAD1,8);return QRCodeModel.createBytes(n,o)},QRCodeModel.createBytes=function(t,e){for(var r=0,o=0,n=0,i=new Array(e.length),a=new Array(e.length),s=0;s<e.length;s++){var h=e[s].dataCount,l=e[s].totalCount-h;o=Math.max(o,h),n=Math.max(n,l),i[s]=new Array(h);for(var u=0;u<i[s].length;u++)i[s][u]=255&t.buffer[u+r];r+=h;var g=QRUtil.getErrorCorrectPolynomial(l),d=new QRPolynomial(i[s],g.getLength()-1).mod(g);a[s]=new Array(g.getLength()-1);for(u=0;u<a[s].length;u++){var f=u+d.getLength()-a[s].length;a[s][u]=f>=0?d.get(f):0}}var c=0;for(u=0;u<e.length;u++)c+=e[u].totalCount;var R=new Array(c),p=0;for(u=0;u<o;u++)for(s=0;s<e.length;s++)u<i[s].length&&(R[p++]=i[s][u]);for(u=0;u<n;u++)for(s=0;s<e.length;s++)u<a[s].length&&(R[p++]=a[s][u]);return R};for(var QRMode={MODE_NUMBER:1,MODE_ALPHA_NUM:2,MODE_8BIT_BYTE:4,MODE_KANJI:8},QRErrorCorrectLevel={L:1,M:0,Q:3,H:2},QRMaskPattern={PATTERN000:0,PATTERN001:1,PATTERN010:2,PATTERN011:3,PATTERN100:4,PATTERN101:5,PATTERN110:6,PATTERN111:7},QRUtil={PATTERN_POSITION_TABLE:[[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],[6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],[6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],[6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],[6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,114,142],[6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,80,106,132,158],[6,32,58,84,110,136,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]],G15:1335,G18:7973,G15_MASK:21522,getBCHTypeInfo:function(t){for(var e=t<<10;QRUtil.getBCHDigit(e)-QRUtil.getBCHDigit(QRUtil.G15)>=0;)e^=QRUtil.G15<<QRUtil.getBCHDigit(e)-QRUtil.getBCHDigit(QRUtil.G15);return(t<<10|e)^QRUtil.G15_MASK},getBCHTypeNumber:function(t){for(var e=t<<12;QRUtil.getBCHDigit(e)-QRUtil.getBCHDigit(QRUtil.G18)>=0;)e^=QRUtil.G18<<QRUtil.getBCHDigit(e)-QRUtil.getBCHDigit(QRUtil.G18);return t<<12|e},getBCHDigit:function(t){for(var e=0;0!=t;)e++,t>>>=1;return e},getPatternPosition:function(t){return QRUtil.PATTERN_POSITION_TABLE[t-1]},getMask:function(t,e,r){switch(t){case QRMaskPattern.PATTERN000:return(e+r)%2==0;case QRMaskPattern.PATTERN001:return e%2==0;case QRMaskPattern.PATTERN010:return r%3==0;case QRMaskPattern.PATTERN011:return(e+r)%3==0;case QRMaskPattern.PATTERN100:return(Math.floor(e/2)+Math.floor(r/3))%2==0;case QRMaskPattern.PATTERN101:return e*r%2+e*r%3==0;case QRMaskPattern.PATTERN110:return(e*r%2+e*r%3)%2==0;case QRMaskPattern.PATTERN111:return(e*r%3+(e+r)%2)%2==0;default:throw new Error("bad maskPattern:"+t)}},getErrorCorrectPolynomial:function(t){for(var e=new QRPolynomial([1],0),r=0;r<t;r++)e=e.multiply(new QRPolynomial([1,QRMath.gexp(r)],0));return e},getLengthInBits:function(t,e){if(1<=e&&e<10)switch(t){case QRMode.MODE_NUMBER:return 10;case QRMode.MODE_ALPHA_NUM:return 9;case QRMode.MODE_8BIT_BYTE:case QRMode.MODE_KANJI:return 8;default:throw new Error("mode:"+t)}else if(e<27)switch(t){case QRMode.MODE_NUMBER:return 12;case QRMode.MODE_ALPHA_NUM:return 11;case QRMode.MODE_8BIT_BYTE:return 16;case QRMode.MODE_KANJI:return 10;default:throw new Error("mode:"+t)}else{if(!(e<41))throw new Error("type:"+e);switch(t){case QRMode.MODE_NUMBER:return 14;case QRMode.MODE_ALPHA_NUM:return 13;case QRMode.MODE_8BIT_BYTE:return 16;case QRMode.MODE_KANJI:return 12;default:throw new Error("mode:"+t)}}},getLostPoint:function(t){for(var e=t.getModuleCount(),r=0,o=0;o<e;o++)for(var n=0;n<e;n++){for(var i=0,a=t.isDark(o,n),s=-1;s<=1;s++)if(!(o+s<0||e<=o+s))for(var h=-1;h<=1;h++)n+h<0||e<=n+h||0==s&&0==h||a==t.isDark(o+s,n+h)&&i++;i>5&&(r+=3+i-5)}for(o=0;o<e-1;o++)for(n=0;n<e-1;n++){var l=0;t.isDark(o,n)&&l++,t.isDark(o+1,n)&&l++,t.isDark(o,n+1)&&l++,t.isDark(o+1,n+1)&&l++,0!=l&&4!=l||(r+=3)}for(o=0;o<e;o++)for(n=0;n<e-6;n++)t.isDark(o,n)&&!t.isDark(o,n+1)&&t.isDark(o,n+2)&&t.isDark(o,n+3)&&t.isDark(o,n+4)&&!t.isDark(o,n+5)&&t.isDark(o,n+6)&&(r+=40);for(n=0;n<e;n++)for(o=0;o<e-6;o++)t.isDark(o,n)&&!t.isDark(o+1,n)&&t.isDark(o+2,n)&&t.isDark(o+3,n)&&t.isDark(o+4,n)&&!t.isDark(o+5,n)&&t.isDark(o+6,n)&&(r+=40);var u=0;for(n=0;n<e;n++)for(o=0;o<e;o++)t.isDark(o,n)&&u++;return r+=10*(Math.abs(100*u/e/e-50)/5)}},QRMath={glog:function(t){if(t<1)throw new Error("glog("+t+")");return QRMath.LOG_TABLE[t]},gexp:function(t){for(;t<0;)t+=255;for(;t>=256;)t-=255;return QRMath.EXP_TABLE[t]},EXP_TABLE:new Array(256),LOG_TABLE:new Array(256)},i=0;i<8;i++)QRMath.EXP_TABLE[i]=1<<i;for(i=8;i<256;i++)QRMath.EXP_TABLE[i]=QRMath.EXP_TABLE[i-4]^QRMath.EXP_TABLE[i-5]^QRMath.EXP_TABLE[i-6]^QRMath.EXP_TABLE[i-8];for(i=0;i<255;i++)QRMath.LOG_TABLE[QRMath.EXP_TABLE[i]]=i;function QRPolynomial(t,e){if(null==t.length)throw new Error(t.length+"/"+e);for(var r=0;r<t.length&&0==t[r];)r++;this.num=new Array(t.length-r+e);for(var o=0;o<t.length-r;o++)this.num[o]=t[o+r]}function QRRSBlock(t,e){this.totalCount=t,this.dataCount=e}function QRBitBuffer(){this.buffer=[],this.length=0}QRPolynomial.prototype={get:function(t){return this.num[t]},getLength:function(){return this.num.length},multiply:function(t){for(var e=new Array(this.getLength()+t.getLength()-1),r=0;r<this.getLength();r++)for(var o=0;o<t.getLength();o++)e[r+o]^=QRMath.gexp(QRMath.glog(this.get(r))+QRMath.glog(t.get(o)));return new QRPolynomial(e,0)},mod:function(t){if(this.getLength()-t.getLength()<0)return this;for(var e=QRMath.glog(this.get(0))-QRMath.glog(t.get(0)),r=new Array(this.getLength()),o=0;o<this.getLength();o++)r[o]=this.get(o);for(o=0;o<t.getLength();o++)r[o]^=QRMath.gexp(QRMath.glog(t.get(o))+e);return new QRPolynomial(r,0).mod(t)}},QRRSBlock.RS_BLOCK_TABLE=[[1,26,19],[1,26,16],[1,26,13],[1,26,9],[1,44,34],[1,44,28],[1,44,22],[1,44,16],[1,70,55],[1,70,44],[2,35,17],[2,35,13],[1,100,80],[2,50,32],[2,50,24],[4,25,9],[1,134,108],[2,67,43],[2,33,15,2,34,16],[2,33,11,2,34,12],[2,86,68],[4,43,27],[4,43,19],[4,43,15],[2,98,78],[4,49,31],[2,32,14,4,33,15],[4,39,13,1,40,14],[2,121,97],[2,60,38,2,61,39],[4,40,18,2,41,19],[4,40,14,2,41,15],[2,146,116],[3,58,36,2,59,37],[4,36,16,4,37,17],[4,36,12,4,37,13],[2,86,68,2,87,69],[4,69,43,1,70,44],[6,43,19,2,44,20],[6,43,15,2,44,16],[4,101,81],[1,80,50,4,81,51],[4,50,22,4,51,23],[3,36,12,8,37,13],[2,116,92,2,117,93],[6,58,36,2,59,37],[4,46,20,6,47,21],[7,42,14,4,43,15],[4,133,107],[8,59,37,1,60,38],[8,44,20,4,45,21],[12,33,11,4,34,12],[3,145,115,1,146,116],[4,64,40,5,65,41],[11,36,16,5,37,17],[11,36,12,5,37,13],[5,109,87,1,110,88],[5,65,41,5,66,42],[5,54,24,7,55,25],[11,36,12],[5,122,98,1,123,99],[7,73,45,3,74,46],[15,43,19,2,44,20],[3,45,15,13,46,16],[1,135,107,5,136,108],[10,74,46,1,75,47],[1,50,22,15,51,23],[2,42,14,17,43,15],[5,150,120,1,151,121],[9,69,43,4,70,44],[17,50,22,1,51,23],[2,42,14,19,43,15],[3,141,113,4,142,114],[3,70,44,11,71,45],[17,47,21,4,48,22],[9,39,13,16,40,14],[3,135,107,5,136,108],[3,67,41,13,68,42],[15,54,24,5,55,25],[15,43,15,10,44,16],[4,144,116,4,145,117],[17,68,42],[17,50,22,6,51,23],[19,46,16,6,47,17],[2,139,111,7,140,112],[17,74,46],[7,54,24,16,55,25],[34,37,13],[4,151,121,5,152,122],[4,75,47,14,76,48],[11,54,24,14,55,25],[16,45,15,14,46,16],[6,147,117,4,148,118],[6,73,45,14,74,46],[11,54,24,16,55,25],[30,46,16,2,47,17],[8,132,106,4,133,107],[8,75,47,13,76,48],[7,54,24,22,55,25],[22,45,15,13,46,16],[10,142,114,2,143,115],[19,74,46,4,75,47],[28,50,22,6,51,23],[33,46,16,4,47,17],[8,152,122,4,153,123],[22,73,45,3,74,46],[8,53,23,26,54,24],[12,45,15,28,46,16],[3,147,117,10,148,118],[3,73,45,23,74,46],[4,54,24,31,55,25],[11,45,15,31,46,16],[7,146,116,7,147,117],[21,73,45,7,74,46],[1,53,23,37,54,24],[19,45,15,26,46,16],[5,145,115,10,146,116],[19,75,47,10,76,48],[15,54,24,25,55,25],[23,45,15,25,46,16],[13,145,115,3,146,116],[2,74,46,29,75,47],[42,54,24,1,55,25],[23,45,15,28,46,16],[17,145,115],[10,74,46,23,75,47],[10,54,24,35,55,25],[19,45,15,35,46,16],[17,145,115,1,146,116],[14,74,46,21,75,47],[29,54,24,19,55,25],[11,45,15,46,46,16],[13,145,115,6,146,116],[14,74,46,23,75,47],[44,54,24,7,55,25],[59,46,16,1,47,17],[12,151,121,7,152,122],[12,75,47,26,76,48],[39,54,24,14,55,25],[22,45,15,41,46,16],[6,151,121,14,152,122],[6,75,47,34,76,48],[46,54,24,10,55,25],[2,45,15,64,46,16],[17,152,122,4,153,123],[29,74,46,14,75,47],[49,54,24,10,55,25],[24,45,15,46,46,16],[4,152,122,18,153,123],[13,74,46,32,75,47],[48,54,24,14,55,25],[42,45,15,32,46,16],[20,147,117,4,148,118],[40,75,47,7,76,48],[43,54,24,22,55,25],[10,45,15,67,46,16],[19,148,118,6,149,119],[18,75,47,31,76,48],[34,54,24,34,55,25],[20,45,15,61,46,16]],QRRSBlock.getRSBlocks=function(t,e){var r=QRRSBlock.getRsBlockTable(t,e);if(null==r)throw new Error("bad rs block @ typeNumber:"+t+"/errorCorrectLevel:"+e);for(var o=r.length/3,n=[],i=0;i<o;i++)for(var a=r[3*i+0],s=r[3*i+1],h=r[3*i+2],l=0;l<a;l++)n.push(new QRRSBlock(s,h));return n},QRRSBlock.getRsBlockTable=function(t,e){switch(e){case QRErrorCorrectLevel.L:return QRRSBlock.RS_BLOCK_TABLE[4*(t-1)+0];case QRErrorCorrectLevel.M:return QRRSBlock.RS_BLOCK_TABLE[4*(t-1)+1];case QRErrorCorrectLevel.Q:return QRRSBlock.RS_BLOCK_TABLE[4*(t-1)+2];case QRErrorCorrectLevel.H:return QRRSBlock.RS_BLOCK_TABLE[4*(t-1)+3];default:return}},QRBitBuffer.prototype={get:function(t){var e=Math.floor(t/8);return 1==(this.buffer[e]>>>7-t%8&1)},put:function(t,e){for(var r=0;r<e;r++)this.putBit(1==(t>>>e-r-1&1))},getLengthInBits:function(){return this.length},putBit:function(t){var e=Math.floor(this.length/8);this.buffer.length<=e&&this.buffer.push(0),t&&(this.buffer[e]|=128>>>this.length%8),this.length++}};var QRCodeLimitLength=[[17,14,11,7],[32,26,20,14],[53,42,32,24],[78,62,46,34],[106,84,60,44],[134,106,74,58],[154,122,86,64],[192,152,108,84],[230,180,130,98],[271,213,151,119],[321,251,177,137],[367,287,203,155],[425,331,241,177],[458,362,258,194],[520,412,292,220],[586,450,322,250],[644,504,364,280],[718,560,394,310],[792,624,442,338],[858,666,482,382],[929,711,509,403],[1003,779,565,439],[1091,857,611,461],[1171,911,661,511],[1273,997,715,535],[1367,1059,751,593],[1465,1125,805,625],[1528,1190,868,658],[1628,1264,908,698],[1732,1370,982,742],[1840,1452,1030,790],[1952,1538,1112,842],[2068,1628,1168,898],[2188,1722,1228,958],[2303,1809,1283,983],[2431,1911,1351,1051],[2563,1989,1423,1093],[2699,2099,1499,1139],[2809,2213,1579,1219],[2953,2331,1663,1273]];function QRCode(t){if(this.options={padding:4,width:256,height:256,typeNumber:4,color:"#000000",background:"#ffffff",ecl:"M"},"string"==typeof t&&(t={content:t}),t)for(var e in t)this.options[e]=t[e];if("string"!=typeof this.options.content)throw new Error("Expected 'content' as string!");if(0===this.options.content.length)throw new Error("Expected 'content' to be non-empty!");if(!(this.options.padding>=0))throw new Error("Expected 'padding' value to be non-negative!");if(!(this.options.width>0&&this.options.height>0))throw new Error("Expected 'width' or 'height' value to be higher than zero!");var r=this.options.content,o=function(t,e){for(var r=function(t){var e=encodeURI(t).toString().replace(/\%[0-9a-fA-F]{2}/g,"a");return e.length+(e.length!=t?3:0)}(t),o=1,n=0,i=0,a=QRCodeLimitLength.length;i<=a;i++){var s=QRCodeLimitLength[i];if(!s)throw new Error("Content too long: expected "+n+" but got "+r);switch(e){case"L":n=s[0];break;case"M":n=s[1];break;case"Q":n=s[2];break;case"H":n=s[3];break;default:throw new Error("Unknwon error correction level: "+e)}if(r<=n)break;o++}if(o>QRCodeLimitLength.length)throw new Error("Content too long");return o}(r,this.options.ecl),n=function(t){switch(t){case"L":return QRErrorCorrectLevel.L;case"M":return QRErrorCorrectLevel.M;case"Q":return QRErrorCorrectLevel.Q;case"H":return QRErrorCorrectLevel.H;default:throw new Error("Unknwon error correction level: "+t)}}(this.options.ecl);this.qrcode=new QRCodeModel(o,n),this.qrcode.addData(r),this.qrcode.make()}QRCode.prototype.svg=function(t){var e=this.options||{},r=this.qrcode.modules;void 0===t&&(t={container:e.container||"svg"});for(var o=void 0===e.pretty||!!e.pretty,n=o?"  ":"",i=o?"\r\n":"",a=e.width,s=e.height,h=r.length,l=a/(h+2*e.padding),u=s/(h+2*e.padding),g=void 0!==e.join&&!!e.join,d=void 0!==e.swap&&!!e.swap,f=void 0===e.xmlDeclaration||!!e.xmlDeclaration,c=void 0!==e.predefined&&!!e.predefined,R=c?n+'<defs><path id="qrmodule" d="M0 0 h'+u+" v"+l+' H0 z" style="fill:'+e.color+';shape-rendering:crispEdges;" /></defs>'+i:"",p=n+'<rect x="0" y="0" width="'+a+'" height="'+s+'" style="fill:'+e.background+';shape-rendering:crispEdges;"/>'+i,m="",Q="",v=0;v<h;v++)for(var E=0;E<h;E++){if(r[E][v]){var M=E*l+e.padding*l,C=v*u+e.padding*u;if(d){var B=M;M=C,C=B}if(g){var w=l+M,L=u+C;M=Number.isInteger(M)?Number(M):M.toFixed(2),C=Number.isInteger(C)?Number(C):C.toFixed(2),w=Number.isInteger(w)?Number(w):w.toFixed(2),Q+="M"+M+","+C+" V"+(L=Number.isInteger(L)?Number(L):L.toFixed(2))+" H"+w+" V"+C+" H"+M+" Z "}else m+=c?n+'<use x="'+M.toString()+'" y="'+C.toString()+'" href="#qrmodule" />'+i:n+'<rect x="'+M.toString()+'" y="'+C.toString()+'" width="'+l+'" height="'+u+'" style="fill:'+e.color+';shape-rendering:crispEdges;"/>'+i}}g&&(m=n+'<path x="0" y="0" style="fill:'+e.color+';shape-rendering:crispEdges;" d="'+Q+'" />');var T="";switch(t.container){case"svg":f&&(T+='<?xml version="1.0" standalone="yes"?>'+i),T+='<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="'+a+'" height="'+s+'">'+i,T+=R+p+m,T+="</svg>";break;case"svg-viewbox":f&&(T+='<?xml version="1.0" standalone="yes"?>'+i),T+='<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 '+a+" "+s+'">'+i,T+=R+p+m,T+="</svg>";break;case"g":T+='<g width="'+a+'" height="'+s+'">'+i,T+=R+p+m,T+="</g>";break;default:T+=(R+p+m).replace(/^\s+/,"")}return T},QRCode.prototype.save=function(t,e){var r=this.svg();"function"!=typeof e&&(e=function(t,e){});try{require("fs").writeFile(t,r,e)}catch(t){e(t)}},"undefined"!=typeof module&&(module.exports=QRCode);
    return QRCode;
  })();
  const I18N = {
    en: {
      appName: "Task Manager",
      chores: "Tasks & Chores",
      openTasksCount: "{count} open tasks",
      calendar: "Calendar",
      things: "Things",
      leaderboard: "Leaderboard",
      settings: "Settings",
      mountMode: "Tablet Mode",
      exitMountMode: "Standard View",
      addTask: "New Chore",
      editTask: "Edit Chore",
      addThing: "New Thing",
      editThing: "Edit Thing",
      addUser: "New Member",
      editUser: "Edit Member",
      addLabel: "New Label",
      editLabel: "Edit Label",
      all: "All",
      today: "Today",
      upcoming: "Upcoming",
      overdue: "Overdue",
      completed: "Completed",
      searchPlaceholder: "Search tasks or chores...",
      noTasks: "No tasks found in this view.",
      noThings: "No tracked things yet. Add items like water filters, vacuum bins, or coffee machines!",
      thingsSubtitle: "Track appliances, filter lifespans, and supplies. Connected chores auto-reset these meters!",
      categoryGeneral: "General",
      lastReset: "Last reset",
      priority: "Priority",
      priorityNone: "None",
      priorityP1: "P1 (Urgent - Red)",
      priorityP2: "P2 (High - Orange)",
      priorityP3: "P3 (Medium - Blue)",
      priorityP4: "P4 (Low - Gray)",
      due: "Due",
      dueDate: "Due Date",
      dueTime: "Due Time",
      assignee: "Assignee",
      label: "Label",
      rotation: "Rotation",
      subtasks: "Subtasks",
      autoResets: "auto-resets",
      points: "Points",
      pointsReward: "Points Reward",
      pts: "pts",
      linkedThing: "Linked Thing",
      save: "Save",
      cancel: "Cancel",
      delete: "Delete",
      edit: "Edit",
      reset: "Reset",
      undo: "Undo",
      done: "Done!",
      recurrence: "Recurrence",
      recurrenceSchedule: "Recurrence (Smart Schedule)",
      recurrenceCadence: "Recurrence Cadence",
      cadenceDueDate: "From Scheduled Due Date (Fixed Cadence)",
      cadenceCompletionDate: "From Actual Completion Date (Adaptive)",
      type: "Type",
      interval: "Interval",
      none: "None",
      noneFixed: "None (Fixed)",
      roundRobin: "Round-Robin",
      leastCompleted: "Least Completed",
      random: "Random",
      round_robin: "Round-Robin",
      least_completed: "Least Completed",
      daily: "Daily",
      weekly: "Weekly",
      monthly: "Monthly",
      yearly: "Yearly",
      customDays: "Every X Days",
      custom_days: "Every X Days",
      streak: "Streak",
      completedChores: "Completed",
      exportBackup: "Export Backup (JSON)",
      importBackup: "Import Backup",
      confirmDelete: "Are you sure you want to delete this?",
      soundEnabled: "Completion Sounds",
      confettiEnabled: "Celebration Confetti",
      gamificationEnabled: "Gamification & Points",
      gamificationDisabledTitle: "Gamification is Disabled",
      gamificationDisabledDesc: "Points, streaks, and leaderboards are currently switched off in settings.",
      defaultPoints: "Default Points per Task",
      firstDayOfWeek: "First Day of Week",
      monday: "Monday",
      sunday: "Sunday",
      recentActivity: "Recent Activity",
      by: "by",
      noRecentActivity: "No recent activity yet.",
      leaderboardAndStreaks: "Leaderboard & Streaks",
      dayStreak: "day streak",
      tasksDone: "tasks done",
      autoTask: "Auto-creates task when limit reached",
      statusNormal: "Normal",
      statusWarning: "Nearing limit",
      statusAlert: "Limit reached!",
      menuToggle: "Toggle sidebar",
      activeMember: "Active Member",
      months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
      weekdays: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      more: "more",
      choresDueOn: "Chores due on",
      noChoresDueOnDate: "No chores due on this date.",
      householdMembers: "Household Members",
      labelsAndCategories: "Labels & Categories",
      preferences: "Preferences",
      language: "Language",
      langAuto: "Auto (Home Assistant)",
      langEn: "English",
      langDe: "Deutsch",
      backupAndRestore: "Data Backup & Restore",
      backupDescription: "Download a complete JSON export of all your tasks, things, users, and history, or restore from a backup.",
      prefSaved: "Preferences saved!",
      backupSuccess: "Backup imported successfully!",
      backupError: "Failed to parse JSON backup file",
      titleRequired: "Title is required!",
      nameRequired: "Name is required!",
      titleLabel: "Title *",
      titlePlaceholder: "e.g. Clean kitchen counters",
      descriptionLabel: "Description",
      descriptionPlaceholder: "Optional notes...",
      subtasksHint: "Subtasks (Automatically resets on completion!)",
      newSubtaskPlaceholder: "New subtask step...",
      addSubtaskStep: "+ Add Subtask Step",
      thingNameLabel: "Name *",
      thingNamePlaceholder: "e.g. Robot Vacuum Dustbin",
      categoryLabel: "Category",
      categoryPlaceholder: "Kitchen, Living room...",
      unitLabel: "Unit of measurement",
      unitPlaceholder: "days, runs, hours, L...",
      currentValue: "Current Value",
      targetValue: "Target / Max Limit",
      autoTaskTitleLabel: "Auto-Generated Task Title",
      autoTaskTitlePlaceholder: "e.g. Empty Robot Vacuum Dustbin",
      memberNameLabel: "Member Name *",
      memberNamePlaceholder: "e.g. Alex",
      colorTheme: "Color Theme",
      labelNameLabel: "Label Name *",
      labelNamePlaceholder: "e.g. Garden",
      colorLabel: "Color",
      providers: "External Providers",
      providersSubtitle: "Link external Home Assistant to-do lists (Google Tasks, Todoist, CalDAV, Local To-do, Bring, Shopping List) to sync tasks seamlessly into Task Manager.",
      linkProvider: "Link Provider",
      unlinkProvider: "Unlink",
      syncProviders: "Sync Now",
      syncSuccess: "Providers synchronized successfully!",
      noProvidersLinked: "No external providers linked yet.",
      selectTodoEntity: "Select Home Assistant To-do Entity",
      providerName: "Provider Display Name",
      filterProvider: "List",
      allLists: "All Lists",
      taskManagerList: "Task Manager (Native)",
      destinationList: "Target List / Provider",
      calendarSyncHint: "Task Manager chores are automatically available in your Home Assistant Calendar under 'Task Manager Chores'.",
      externalTask: "External",
      loadingEntities: "Loading available entities...",
      noEntitiesFound: "No other to-do entities found in Home Assistant.",
      enterManually: "Enter manually",
      chooseFromList: "Select from list",
      manualEntityId: "To-do Entity ID (e.g. todo.shopping_list)",
      enterManuallyHint: "You can enter your entity ID directly:",
      selectOrEnterEntity: "Please select or enter a valid to-do entity ID",
      mustStartWithTodo: "Entity ID must start with 'todo.' (e.g. todo.shopping_list)",
      optional: "optional",
      linkedEntity: "Linked Home Assistant Entity (optional)",
      linkedEntityPlaceholder: "Search or enter entity (e.g. sensor.vacuum_filter)",
      linkedEntityHint: "Automatically syncs this Thing's value with an external numeric sensor.",
      thresholdCondition: "Trigger Condition",
      thresholdOperatorGte: "≥ Greater than or equal (counts up, e.g. filter days)",
      thresholdOperatorLte: "≤ Less than or equal (counts down, e.g. remaining brush %)",
      thresholdValue: "Trigger Threshold Value",
      taskLinkedThingHint: "⚡ This task is linked to a Thing with threshold. It becomes due on the day the threshold is reached. A schedule is optional as a fallback.",
      waitingForThreshold: "Waiting for threshold",
      thresholdTriggered: "Threshold reached",
      completionScript: "Completion Script (optional)",
      completionScriptPlaceholder: "Search or enter script (e.g. script.reset_vacuum)",
      completionScriptHint: "Home Assistant script automatically executed when a linked task is completed (e.g. to reset counters).",
      searchEntityPlaceholder: "Search entity by name or ID...",
      noMatchingEntities: "No matching entities found",
      clearSelection: "Clear",
      duplicate: "Duplicate",
      dueSoon: "Due Soon",
      reminders: "Reminders",
      weekdaysLabel: "Repeat on Weekdays",
      atDueTime: "At due time",
      minBefore: "{min}m before",
      hoursBefore: "{hours}h before",
      daysBefore: "{days}d before",
      tags: "Tags",
      tagsPlaceholder: "e.g. kitchen, trash, weekly (comma separated)",
      dependencies: "Dependencies",
      dependenciesHint: "Select prerequisite tasks that must be done first",
      dueSoonDays: "Due Soon Threshold (days)",
      notificationInterval: "Notification Interval (days)",
      isActive: "Task Active",
      isPaused: "Paused",
      pause: "Pause Task",
      resume: "Resume Task",
      pauseTask: "Pause Task",
      resumeTask: "Resume Task",
      taskPaused: "Task \"{title}\" paused",
      taskResumed: "Task \"{title}\" resumed",
      timesCompleted: "{count}x completed",
      repeatMode: "Recurrence Mode",
      repeatModeAfter: "Interval after completion",
      repeatModeEvery: "Calendar Schedule",
      repeatEveryWeekday: "Specific Weekday",
      repeatEveryDayOfMonth: "Day of Month",
      repeatEveryWeekdayOfMonth: "Nth Weekday of Month",
      repeatEveryDaysBeforeEndOfMonth: "Days before month end",
      activeOverride: "HA Active Override Entity (optional)",
      intervalOverride: "HA Interval Override Entity (optional)",
      dueSoonOverride: "HA Due-Soon Override Entity (optional)",
      setLastDoneDate: "Set Completion Date",
      lastDoneDate: "Last Done Date",
      advancedOptions: "Advanced & Overrides",
      parts: "Spare Parts & Supplies",
      addPart: "New Spare Part",
      editPart: "Edit Spare Part",
      deletePart: "Delete Spare Part",
      partNameLabel: "Part Name *",
      partNamePlaceholder: "e.g. HEPA Filter, Mop Pad, Water Filter",
      partNumberLabel: "Part Number / SKU",
      partNumberPlaceholder: "e.g. HF-2024-X",
      stockLabel: "Current Stock",
      minStockLabel: "Min Stock / Reorder Threshold",
      unitPriceLabel: "Unit Price / Cost",
      storageLocationLabel: "Storage Location",
      storageLocationPlaceholder: "e.g. Basement Shelf 2, Utility Closet",
      reorderUrlLabel: "Reorder Web Link",
      reorderUrlPlaceholder: "https://amazon.com/...",
      reorder: "Reorder",
      lowStock: "Low Stock!",
      inStock: "In Stock",
      noParts: "No spare parts recorded yet. Add items like HEPA filters, detergent, bags, or oils!",
      partsSubtitle: "Track supplies and spare parts inventory. Automatic stock deduction and reorder warnings when completing maintenance!",
      warranty: "Warranty",
      warrantyValid: "Warranty Valid",
      warrantyExpiringSoon: "Warranty Expiring Soon",
      warrantyExpired: "Warranty Expired",
      warrantyExpiryLabel: "Warranty Expiry Date",
      installationDateLabel: "Installation / Purchase Date",
      manufacturerLabel: "Manufacturer",
      manufacturerPlaceholder: "e.g. Miele, Roborock, Bosch",
      modelLabel: "Model",
      modelPlaceholder: "e.g. S7 MaxV Ultra",
      serialNumberLabel: "Serial Number",
      serialNumberPlaceholder: "e.g. SN-987654321",
      documentationUrlLabel: "Manual / Documentation Link",
      documentationUrlPlaceholder: "https://...",
      viewManual: "Manual",
      taskTypeLabel: "Task Type",
      taskTypeChore: "Maintenance / Regular Chore",
      taskTypeReading: "Meter / Utility Reading",
      readingUnitLabel: "Reading Unit (e.g. m³, kWh, L, bar)",
      lastReadingLabel: "Last Reading Value",
      readingValueLabel: "Current Meter Reading",
      consumptionDelta: "Consumption / Delta",
      consumedPartsLabel: "Consumed Spare Parts",
      durationMinutesLabel: "Duration (minutes)",
      costLabel: "Total Cost (€ / $)",
      notesLabel: "Notes / Work Log",
      completedAtLabel: "Completion Date & Time",
      completeWithDetails: "Complete with Details",
      skip: "Skip",
      skipTask: "Skip Task",
      skipConfirm: "Skip this task recurrence? Next due date will be calculated without awarding points.",
      onCompleteEntityLabel: "Action Entity on Completion (button/script/switch)",
      onCompleteEntityPlaceholder: "e.g. button.vacuum_start or script.clean",
      qrCode: "QR Code",
      scanQr: "Scan with smartphone camera or Home Assistant Companion App",
      qrTaskSubtitle: "Scan with camera to complete this task immediately.",
      qrThingSubtitle: "Scan with camera to view maintenance tasks for this appliance.",
      printTag: "Print Label",
      copyLink: "Copy Link",
      linkCopied: "Link copied to clipboard!",
      targetUrl: "Target URL",
      taskCompleted: "Task \"{title}\" completed! 🎉",
      taskCompletedViaQr: "Task \"{title}\" completed via QR-Code! 🎉",
      recurringTaskCompleted: "Task \"{title}\" completed! Next due date: {nextDue} 🔄🎉",
      recurringTaskCompletedViaQr: "Task \"{title}\" completed via QR-Code! Next due date: {nextDue} 🔄🎉",
      taskAlreadyCompleted: "Task \"{title}\" is already completed.",
      qrLocalhostWarning: "Note: You are connected via \"localhost\". To scan this QR code with a smartphone, open Home Assistant using your network IP (e.g. http://192.168.x.x:8123) or domain.",
      justCompletedBadge: "Done just now! Next: {nextDue}",
      doneToday: "Done today",
      close: "Close",
    },
    de: {
      appName: "Task Manager",
      chores: "Aufgaben & Chores",
      openTasksCount: "{count} offene Aufgaben",
      calendar: "Kalender",
      things: "Things",
      leaderboard: "Bestenliste",
      settings: "Einstellungen",
      mountMode: "Tablet-Modus",
      exitMountMode: "Standardansicht",
      addTask: "Neue Aufgabe",
      editTask: "Aufgabe bearbeiten",
      addThing: "Neues Thing",
      editThing: "Thing bearbeiten",
      addUser: "Neues Mitglied",
      editUser: "Mitglied bearbeiten",
      addLabel: "Neues Label",
      editLabel: "Label bearbeiten",
      all: "Alle",
      today: "Heute",
      upcoming: "Demnächst",
      overdue: "Überfällig",
      completed: "Erledigt",
      searchPlaceholder: "Aufgaben durchsuchen...",
      noTasks: "Keine Aufgaben in dieser Ansicht.",
      noThings: "Noch keine Things hinterlegt. Erfasse Haushaltsgeräte wie Wasserfilter, Staubsauger oder Kaffeemaschine!",
      thingsSubtitle: "Verfolge Haushaltsgeräte, Filter-Lebensdauern und Verbrauchsgüter. Verknüpfte Aufgaben setzen diese Zähler automatisch zurück!",
      categoryGeneral: "Allgemein",
      lastReset: "Zuletzt zurückgesetzt",
      priority: "Priorität",
      priorityNone: "Keine",
      priorityP1: "P1 (Dringend - Rot)",
      priorityP2: "P2 (Hoch - Orange)",
      priorityP3: "P3 (Mittel - Blau)",
      priorityP4: "P4 (Niedrig - Grau)",
      due: "Fällig",
      dueDate: "Fälligkeitsdatum",
      dueTime: "Fälligkeitszeit",
      assignee: "Zuständig",
      label: "Label",
      rotation: "Rotation",
      subtasks: "Teilaufgaben",
      autoResets: "automatisch zurückgesetzt",
      points: "Punkte",
      pointsReward: "Punkte-Belohnung",
      pts: "Pkt.",
      linkedThing: "Verknüpftes Thing",
      save: "Speichern",
      cancel: "Abbrechen",
      delete: "Löschen",
      edit: "Bearbeiten",
      reset: "Zurücksetzen",
      undo: "Wiederherstellen",
      done: "Erledigt!",
      recurrence: "Wiederholung",
      recurrenceSchedule: "Wiederholung (Intelligenter Zeitplan)",
      recurrenceCadence: "Wiederholungs-Basis",
      cadenceDueDate: "Ab geplantem Fälligkeitsdatum (Fester Takt)",
      cadenceCompletionDate: "Ab tatsächlichem Erledigungsdatum (Adaptiv)",
      type: "Intervall-Typ",
      interval: "Intervall",
      none: "Keine",
      noneFixed: "Keine (Fest)",
      roundRobin: "Reihum (Round-Robin)",
      leastCompleted: "Wenigste Erledigungen",
      random: "Zufällig",
      round_robin: "Reihum (Round-Robin)",
      least_completed: "Wenigste Erledigungen",
      daily: "Täglich",
      weekly: "Wöchentlich",
      monthly: "Monatlich",
      yearly: "Jährlich",
      customDays: "Alle X Tage",
      custom_days: "Alle X Tage",
      streak: "Serie",
      completedChores: "Erledigt",
      exportBackup: "Backup exportieren (JSON)",
      importBackup: "Backup importieren",
      confirmDelete: "Möchtest du dies wirklich löschen?",
      soundEnabled: "Erledigungs-Sounds",
      confettiEnabled: "Konfetti-Effekt",
      gamificationEnabled: "Gamification & Punkte",
      gamificationDisabledTitle: "Gamification ist deaktiviert",
      gamificationDisabledDesc: "Punkte, Serien und Bestenlisten sind derzeit in den Einstellungen ausgeschaltet.",
      defaultPoints: "Standard-Punkte pro Aufgabe",
      firstDayOfWeek: "Erster Wochentag",
      monday: "Montag",
      sunday: "Sonntag",
      recentActivity: "Letzte Aktivitäten",
      by: "von",
      noRecentActivity: "Noch keine Aktivitäten vorhanden.",
      leaderboardAndStreaks: "Bestenliste & Serien",
      dayStreak: "Tage Serie",
      tasksDone: "Aufgaben erledigt",
      autoTask: "Erstellt automatisch Aufgabe bei Erreichen",
      statusNormal: "Normal",
      statusWarning: "Bald fällig",
      statusAlert: "Limit erreicht!",
      menuToggle: "Seitenleiste ein-/ausblenden",
      activeMember: "Aktives Mitglied",
      months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
      weekdays: ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
      more: "weitere",
      choresDueOn: "Fällige Aufgaben am",
      noChoresDueOnDate: "Keine Aufgaben an diesem Tag fällig.",
      householdMembers: "Haushaltsmitglieder",
      labelsAndCategories: "Labels & Kategorien",
      preferences: "Einstellungen",
      language: "Sprache",
      langAuto: "Automatisch (Home Assistant)",
      langEn: "English",
      langDe: "Deutsch",
      backupAndRestore: "Datensicherung & Wiederherstellung",
      backupDescription: "Lade einen vollständigen JSON-Export aller Aufgaben, Things, Mitglieder und Verläufe herunter oder stelle ein Backup wieder her.",
      prefSaved: "Einstellungen gespeichert!",
      backupSuccess: "Backup erfolgreich importiert!",
      backupError: "Fehler beim Parsen der Backup-Datei",
      titleRequired: "Titel ist erforderlich!",
      nameRequired: "Name ist erforderlich!",
      titleLabel: "Titel *",
      titlePlaceholder: "z. B. Küchenarbeitsplatte reinigen",
      descriptionLabel: "Beschreibung",
      descriptionPlaceholder: "Optionale Notizen...",
      subtasksHint: "Teilaufgaben (Werden bei Wiederholung automatisch zurückgesetzt!)",
      newSubtaskPlaceholder: "Neuer Unterschritt...",
      addSubtaskStep: "+ Teilaufgabe hinzufügen",
      thingNameLabel: "Name *",
      thingNamePlaceholder: "z. B. Staubsauger-Staubbehälter",
      categoryLabel: "Kategorie",
      categoryPlaceholder: "Küche, Wohnzimmer...",
      unitLabel: "Maßeinheit",
      unitPlaceholder: "Tage, Durchläufe, Stunden, L...",
      currentValue: "Aktueller Wert",
      targetValue: "Ziel / Maximalwert",
      autoTaskTitleLabel: "Titel der automatisch erstellten Aufgabe",
      autoTaskTitlePlaceholder: "z. B. Staubsauger-Staubbehälter leeren",
      memberNameLabel: "Name des Mitglieds *",
      memberNamePlaceholder: "z. B. Alex",
      colorTheme: "Farbe",
      labelNameLabel: "Label-Name *",
      labelNamePlaceholder: "z. B. Garten",
      colorLabel: "Farbe",
      providers: "Externe Provider",
      providersSubtitle: "Verknüpfe externe Home Assistant To-do-Listen (Google Tasks, Todoist, CalDAV, Local To-do, Bring, Einkaufsliste), um Aufgaben nahtlos mit Task Manager zu synchronisieren.",
      linkProvider: "Provider verknüpfen",
      unlinkProvider: "Trennen",
      syncProviders: "Jetzt synchronisieren",
      syncSuccess: "Provider erfolgreich synchronisiert!",
      noProvidersLinked: "Noch keine externen Provider verknüpft.",
      selectTodoEntity: "Home Assistant To-do-Entität auswählen",
      providerName: "Provider-Anzeigename",
      filterProvider: "Liste",
      allLists: "Alle Listen",
      taskManagerList: "Task Manager (Nativ)",
      destinationList: "Zielliste / Provider",
      calendarSyncHint: "Task Manager Aufgaben stehen automatisch in deinem Home Assistant Kalender unter 'Task Manager Aufgaben' zur Verfügung.",
      externalTask: "Extern",
      loadingEntities: "Lade verfügbare Entitäten...",
      noEntitiesFound: "Keine weiteren To-do-Entitäten in Home Assistant gefunden.",
      enterManually: "Manuell eingeben",
      chooseFromList: "Aus Liste auswählen",
      manualEntityId: "To-do-Entitäts-ID (z. B. todo.einkaufsliste)",
      enterManuallyHint: "Du kannst die Entitäts-ID direkt manuell eingeben:",
      selectOrEnterEntity: "Bitte wähle eine To-do-Entitäts-ID aus oder gib eine ein",
      mustStartWithTodo: "Die Entitäts-ID muss mit 'todo.' beginnen (z. B. todo.einkaufsliste)",
      optional: "optional",
      linkedEntity: "Verknüpfte Home Assistant Entität (optional)",
      linkedEntityPlaceholder: "Entität suchen oder eingeben (z. B. sensor.vacuum_filter)",
      linkedEntityHint: "Synchronisiert den Wert dieses Things automatisch mit einem externen numerischen Sensor.",
      thresholdCondition: "Trigger-Bedingung",
      thresholdOperatorGte: "≥ Größer oder gleich (Zähler zählt hoch, z. B. Filter-Tage)",
      thresholdOperatorLte: "≤ Kleiner oder gleich (Lebensdauer zählt runter, z. B. Bürsten-Rest %)",
      thresholdValue: "Trigger-Schwellwert",
      taskLinkedThingHint: "⚡ Diese Aufgabe ist an ein Thing mit Schwellwert gekoppelt. Sie wird am Tag der Schwellwert-Überschreitung fällig. Ein Zeitplan ist optional als Fallback.",
      waitingForThreshold: "Wartet auf Schwellwert",
      thresholdTriggered: "Schwellwert erreicht",
      completionScript: "Ausführungsskript bei Erledigung (optional)",
      completionScriptPlaceholder: "Skript suchen oder eingeben (z. B. script.reset_vacuum)",
      completionScriptHint: "Home Assistant Skript, das automatisch ausgeführt wird, sobald eine verknüpfte Aufgabe erledigt wird (z. B. zum Zurücksetzen von Zählern).",
      searchEntityPlaceholder: "Entität nach Name oder ID suchen...",
      noMatchingEntities: "Keine passenden Entitäten gefunden",
      clearSelection: "Löschen",
      duplicate: "Duplizieren",
      dueSoon: "Bald fällig",
      reminders: "Erinnerungen",
      weekdaysLabel: "Wochentage",
      atDueTime: "Pünktlich zum Termin",
      minBefore: "{min} Min. vorher",
      hoursBefore: "{hours} Std. vorher",
      daysBefore: "{days} Tage vorher",
      tags: "Tags",
      tagsPlaceholder: "z.B. küche, müll, wöchentlich (kommagetrennt)",
      dependencies: "Abhängigkeiten",
      dependenciesHint: "Wähle Aufgaben aus, die zuerst erledigt sein müssen",
      dueSoonDays: "Bald-fällig-Schwelle (Tage)",
      notificationInterval: "Benachrichtigungsintervall (Tage)",
      isActive: "Aufgabe Aktiv",
      isPaused: "Pausiert",
      pause: "Aufgabe pausieren",
      resume: "Aufgabe fortsetzen",
      pauseTask: "Aufgabe pausieren",
      resumeTask: "Aufgabe fortsetzen",
      taskPaused: "Aufgabe \"{title}\" pausiert",
      taskResumed: "Aufgabe \"{title}\" fortgesetzt",
      timesCompleted: "{count}x erledigt",
      repeatMode: "Wiederholungsmodus",
      repeatModeAfter: "Intervall nach Erledigung",
      repeatModeEvery: "Fester Kalenderplan",
      repeatEveryWeekday: "Bestimmter Wochentag",
      repeatEveryDayOfMonth: "Tag im Monat",
      repeatEveryWeekdayOfMonth: "N-ter Wochentag im Monat",
      repeatEveryDaysBeforeEndOfMonth: "Tage vor Monatsende",
      activeOverride: "HA Aktiv-Override Entität (optional)",
      intervalOverride: "HA Intervall-Override Entität (optional)",
      dueSoonOverride: "HA Bald-Fällig-Override Entität (optional)",
      setLastDoneDate: "Erledigt-Datum manuell setzen",
      lastDoneDate: "Letztes Erledigt-Datum",
      advancedOptions: "Erweitert & HA Overrides",
      parts: "Ersatzteile & Vorrat",
      addPart: "Neues Ersatzteil",
      editPart: "Ersatzteil bearbeiten",
      deletePart: "Ersatzteil löschen",
      partNameLabel: "Bezeichnung *",
      partNamePlaceholder: "z. B. HEPA-Filter, Wischtuch, Entkalker",
      partNumberLabel: "Teilenummer / Artikelnummer",
      partNumberPlaceholder: "z. B. HF-2024-X",
      stockLabel: "Aktueller Bestand",
      minStockLabel: "Mindestbestand / Meldeschwelle",
      unitPriceLabel: "Stückpreis / Kosten",
      storageLocationLabel: "Lagerort",
      storageLocationPlaceholder: "z. B. Keller Regal 2, Hauswirtschaftsraum",
      reorderUrlLabel: "Nachbestell-Link",
      reorderUrlPlaceholder: "https://amazon.de/...",
      reorder: "Nachbestellen",
      lowStock: "Geringer Bestand!",
      inStock: "Auf Lager",
      noParts: "Noch keine Ersatzteile hinterlegt. Erfasse Filter, Beutel, Reinigungsmittel oder Öle!",
      partsSubtitle: "Verwalte Verbrauchsgüter und Ersatzteile. Automatische Bestandsabbuchung und Nachbestell-Warnungen bei Wartungsarbeiten!",
      warranty: "Garantie",
      warrantyValid: "Garantie gültig",
      warrantyExpiringSoon: "Garantie läuft bald ab",
      warrantyExpired: "Garantie abgelaufen",
      warrantyExpiryLabel: "Garantie bis",
      installationDateLabel: "Installations- / Kaufdatum",
      manufacturerLabel: "Hersteller",
      manufacturerPlaceholder: "z. B. Miele, Roborock, Bosch",
      modelLabel: "Modell",
      modelPlaceholder: "z. B. S7 MaxV Ultra",
      serialNumberLabel: "Seriennummer",
      serialNumberPlaceholder: "z. B. SN-987654321",
      documentationUrlLabel: "Handbuch / Doku-Link",
      documentationUrlPlaceholder: "https://...",
      viewManual: "Handbuch",
      taskTypeLabel: "Aufgabentyp",
      taskTypeChore: "Wartung / Reguläre Aufgabe",
      taskTypeReading: "Zählerablesung",
      readingUnitLabel: "Ableseeinheit (z. B. m³, kWh, L, bar)",
      lastReadingLabel: "Letzter Zählerstand",
      readingValueLabel: "Aktueller Zählerstand",
      consumptionDelta: "Verbrauch / Differenz",
      consumedPartsLabel: "Verbrauchte Ersatzteile",
      durationMinutesLabel: "Dauer (Minuten)",
      costLabel: "Gesamtkosten (€)",
      notesLabel: "Notizen / Arbeitsbericht",
      completedAtLabel: "Erledigungszeitpunkt",
      completeWithDetails: "Mit Details erledigen",
      skip: "Überspringen",
      skipTask: "Aufgabe überspringen",
      skipConfirm: "Diese Fälligkeit überspringen? Der nächste Termin wird berechnet, ohne Punkte zu vergeben.",
      onCompleteEntityLabel: "Aktions-Entität bei Erledigung (Button/Skript/Schalter)",
      onCompleteEntityPlaceholder: "z. B. button.vacuum_start oder script.clean",
      qrCode: "QR-Code",
      scanQr: "Mit Smartphone-Kamera oder Home Assistant Companion App scannen",
      qrTaskSubtitle: "Mit Smartphone-Kamera scannen, um diese Aufgabe sofort zu erledigen.",
      qrThingSubtitle: "Mit Smartphone-Kamera scannen, um Wartungsaufgaben für dieses Gerät anzuzeigen.",
      printTag: "Etikett drucken",
      copyLink: "Link kopieren",
      linkCopied: "Link in die Zwischenablage kopiert!",
      targetUrl: "Ziel-URL",
      taskCompleted: "Aufgabe \"{title}\" erledigt! 🎉",
      taskCompletedViaQr: "Aufgabe \"{title}\" via QR-Code erledigt! 🎉",
      recurringTaskCompleted: "Aufgabe \"{title}\" erledigt! Nächste Fälligkeit: {nextDue} 🔄🎉",
      recurringTaskCompletedViaQr: "Aufgabe \"{title}\" via QR-Code erledigt! Nächste Fälligkeit: {nextDue} 🔄🎉",
      taskAlreadyCompleted: "Aufgabe \"{title}\" ist bereits erledigt.",
      qrLocalhostWarning: "Hinweis: Du bist über \"localhost\" verbunden. Um den QR-Code mit dem Smartphone zu scannen, öffne Home Assistant über die Netzwerk-IP (z. B. http://192.168.x.x:8123) oder deine Domain.",
      justCompletedBadge: "Gerade erledigt! Nächste: {nextDue}",
      doneToday: "Heute erledigt",
      close: "Schließen",
    }
  };

  class TaskManagerPanel extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._hass = null;
      this._data = {
        tasks: [],
        things: [],
        users: [],
        labels: [],
        settings: {},
        activity_log: [],
        providers: [],
        parts: []
      };
      this._currentTab = "chores";
      this._filterStatus = "all";
      this._filterAssignee = "all";
      this._filterLabel = "all";
      this._filterPriority = "all";
      this._filterProvider = "all";
      this._searchQuery = "";
      this._activeUser = null;
      this._modalState = null;
      this._calendarDate = new Date();
      this._calendarSelectedDay = null;
      this._tabletMode = false;
      this._audioCtx = null;
      this._availableTodoEntities = [];
      this._urlParamsHandled = false;
      this._justCompletedTaskId = null;
    }

    connectedCallback() {
      this._onResize = () => this._updateSidebarVisibility();
      window.addEventListener("resize", this._onResize);
      this._updateSidebarVisibility();

      this._onLocationChange = () => {
        this._urlParamsHandled = false;
        this._handleUrlParameters();
      };
      window.addEventListener("location-changed", this._onLocationChange);
      window.addEventListener("popstate", this._onLocationChange);
    }

    disconnectedCallback() {
      if (this._onResize) {
        window.removeEventListener("resize", this._onResize);
      }
      if (this._onLocationChange) {
        window.removeEventListener("location-changed", this._onLocationChange);
        window.removeEventListener("popstate", this._onLocationChange);
      }
    }

    _isSidebarHidden() {
      if (!this._hass) return true;
      if (window.innerWidth < 870) {
        return true;
      }
      const docked = this._hass.dockedSidebar;
      if (docked === "docked") {
        return false;
      }
      if (docked === "hidden" || docked === "undocked") {
        return true;
      }
      if (docked === "auto") {
        try {
          const ha = document.querySelector("home-assistant");
          const main = ha && ha.shadowRoot && ha.shadowRoot.querySelector("home-assistant-main");
          if (main && main.shadowRoot) {
            const sidebar = main.shadowRoot.querySelector("ha-sidebar");
            if (sidebar) {
              const rect = sidebar.getBoundingClientRect();
              if (rect.width > 50 && sidebar.offsetParent !== null) {
                return false;
              }
            }
          }
        } catch (e) {}
        return true;
      }
      return true;
    }

    _updateSidebarVisibility() {
      const isHidden = this._isSidebarHidden();
      const menuBtn = this.shadowRoot && this.shadowRoot.getElementById("menu-toggle-btn");
      if (menuBtn) {
        menuBtn.style.display = isHidden ? "inline-flex" : "none";
      }
    }

    set hass(hass) {
      const isFirst = !this._hass;
      const prevDocked = this._hass ? this._hass.dockedSidebar : null;
      this._hass = hass;
      if (isFirst) {
        this._initAudio();
        this._fetchData();
      }
      if (prevDocked !== (hass && hass.dockedSidebar)) {
        this._updateSidebarVisibility();
      }
    }

    get lang() {
      const savedLang = this._data && this._data.settings && this._data.settings.language;
      if (savedLang === "de" || savedLang === "en") return savedLang;
      const l = (this._hass && (this._hass.language || (this._hass.locale && this._hass.locale.language))) || "en";
      return l.startsWith("de") ? "de" : "en";
    }

    t(key, params = null) {
      const langDict = I18N[this.lang] || I18N.en;
      let val = langDict[key] !== undefined ? langDict[key] : (I18N.en[key] !== undefined ? I18N.en[key] : key);
      if (typeof val === "string" && params && typeof params === "object") {
        for (const [k, v] of Object.entries(params)) {
          val = val.replace(new RegExp(`{${k}}`, "g"), v);
        }
      }
      return val;
    }

    _initAudio() {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this._audioCtx = new AudioContext();
        }
      } catch (e) {
        // audio optional
      }
    }

    _playSuccessSound() {
      if (!this._data.settings.sound_enabled || !this._audioCtx) return;
      try {
        if (this._audioCtx.state === "suspended") {
          this._audioCtx.resume();
        }
        const osc = this._audioCtx.createOscillator();
        const gain = this._audioCtx.createGain();
        osc.type = "sine";
        osc.connect(gain);
        gain.connect(this._audioCtx.destination);

        const now = this._audioCtx.currentTime;
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880.0, now + 0.12); // A5
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

        osc.start(now);
        osc.stop(now + 0.35);
      } catch (e) {}
    }

    _triggerConfetti() {
      if (!this._data.settings.confetti_enabled) return;
      const canvas = this.shadowRoot.getElementById("confetti-canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      const particles = [];
      const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

      for (let i = 0; i < 70; i++) {
        particles.push({
          x: canvas.width / 2 + (Math.random() * 200 - 100),
          y: canvas.height / 3 + (Math.random() * 100 - 50),
          vx: (Math.random() - 0.5) * 14,
          vy: Math.random() * -12 - 4,
          color: colors[Math.floor(Math.random() * colors.length)],
          size: Math.random() * 8 + 4,
          rot: Math.random() * 360,
          vrot: (Math.random() - 0.5) * 15,
          alpha: 1
        });
      }

      let animId;
      const render = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        for (const p of particles) {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.45; // gravity
          p.rot += p.vrot;
          p.alpha -= 0.015;

          if (p.alpha > 0) {
            alive = true;
            ctx.save();
            ctx.globalAlpha = p.alpha;
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rot * Math.PI) / 180);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.7);
            ctx.restore();
          }
        }
        if (alive) {
          animId = requestAnimationFrame(render);
        } else {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          cancelAnimationFrame(animId);
        }
      };
      render();
    }

    async _fetchData() {
      if (!this._hass) return;
      try {
        const res = await this._hass.callWS({ type: "task_manager/get_data" });
        if (res) {
          this._data = res;
          this._data.parts = this._data.parts || [];
          this._data.things = this._data.things || [];
          this._data.tasks = this._data.tasks || [];
          this._data.users = this._data.users || [];
          this._data.labels = this._data.labels || [];
          this._data.providers = this._data.providers || [];
          if (this._data.settings && this._data.settings.tablet_mount_mode && !this._tabletMode) {
            this._tabletMode = true;
          }
          if (!this._activeUser && this._data.users && this._data.users.length > 0) {
            this._activeUser = this._data.users[0].id;
          }
          this._render();
          await this._handleUrlParameters();
        }
      } catch (err) {
        console.error("Task Manager: Failed to load data", err);
      }
    }

    async _callWS(type, payload = {}) {
      if (!this._hass) return;
      try {
        const res = await this._hass.callWS({ type, ...payload });
        if (res && res.data) {
          this._data = res.data;
          this._data.parts = this._data.parts || [];
          this._data.things = this._data.things || [];
          this._data.tasks = this._data.tasks || [];
          this._data.users = this._data.users || [];
          this._data.labels = this._data.labels || [];
          this._data.providers = this._data.providers || [];
          this._render();
        } else {
          await this._fetchData();
        }
        return res;
      } catch (err) {
        console.error(`Task Manager: Error calling ${type}`, err);
        alert(`Error: ${err.message || err}`);
        await this._fetchData();
      }
    }

    _showToast(message, type = "success") {
      const existing = this.shadowRoot && this.shadowRoot.getElementById("panel-toast");
      if (existing) existing.remove();

      const toast = document.createElement("div");
      toast.id = "panel-toast";
      toast.style.position = "fixed";
      toast.style.bottom = "28px";
      toast.style.left = "50%";
      toast.style.transform = "translateX(-50%)";
      toast.style.background = type === "error" ? "var(--error-color, #ef4444)" : type === "info" ? "#334155" : "var(--primary-color, #2563eb)";
      toast.style.color = "#ffffff";
      toast.style.padding = "14px 26px";
      toast.style.borderRadius = "12px";
      toast.style.boxShadow = "0 8px 30px rgba(0,0,0,0.35)";
      toast.style.fontSize = "15px";
      toast.style.fontWeight = "600";
      toast.style.zIndex = "99999";
      toast.style.display = "flex";
      toast.style.alignItems = "center";
      toast.style.gap = "10px";
      toast.style.transition = "all 0.3s cubic-bezier(0.16, 1, 0.3, 1)";
      toast.style.pointerEvents = "none";
      toast.textContent = message;

      if (this.shadowRoot) {
        this.shadowRoot.appendChild(toast);
        setTimeout(() => {
          toast.style.opacity = "0";
          toast.style.transform = "translateX(-50%) translateY(12px)";
          setTimeout(() => toast.remove(), 350);
        }, 4000);
      }
    }

    async _copyToClipboard(text) {
      if (navigator.clipboard && window.isSecureContext) {
        try {
          await navigator.clipboard.writeText(text);
          return true;
        } catch (e) {
          console.warn("navigator.clipboard.writeText failed, using fallback", e);
        }
      }

      try {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.top = "-9999px";
        textArea.style.left = "-9999px";
        textArea.style.opacity = "0";
        const container = document.body || document.documentElement || this.shadowRoot;
        if (container) {
          container.appendChild(textArea);
          textArea.focus();
          textArea.select();
          const successful = document.execCommand("copy");
          container.removeChild(textArea);
          if (successful) return true;
        }
      } catch (err) {
        console.error("execCommand fallback failed", err);
      }

      try {
        if (typeof prompt === "function") {
          prompt(this.t("copyLink"), text);
          return true;
        }
      } catch (e) {}
      return false;
    }

    _printTag(title, subtitle, qrSvg, targetUrl) {
      try {
        const oldFrame = document.getElementById("qr-print-frame");
        if (oldFrame) oldFrame.remove();

        const frame = document.createElement("iframe");
        frame.id = "qr-print-frame";
        frame.style.position = "fixed";
        frame.style.top = "-9999px";
        frame.style.left = "-9999px";
        frame.style.width = "1px";
        frame.style.height = "1px";
        frame.style.border = "none";
        const container = document.body || document.documentElement;
        if (container) {
          container.appendChild(frame);
        } else {
          return;
        }

        const frameDoc = frame.contentWindow.document || frame.contentDocument;
        frameDoc.open();
        frameDoc.write(`
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset="utf-8">
              <title>Etikett - ${this._escape(title)}</title>
              <style>
                @page { margin: 8mm; size: auto; }
                body {
                  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                  margin: 0;
                  padding: 16px;
                  display: flex;
                  justify-content: center;
                  background: #fff;
                }
                .tag-card {
                  border: 2px dashed #1e293b;
                  border-radius: 12px;
                  padding: 18px 20px;
                  text-align: center;
                  width: 280px;
                  background: #fff;
                  box-sizing: border-box;
                }
                .tag-title {
                  font-size: 16px;
                  font-weight: 700;
                  color: #0f172a;
                  margin: 0 0 4px 0;
                  line-height: 1.3;
                  word-break: break-word;
                }
                .tag-sub {
                  font-size: 11px;
                  color: #64748b;
                  margin: 0 0 12px 0;
                }
                .qr-box {
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  margin: 0 auto 10px auto;
                }
                .qr-box svg {
                  width: 170px !important;
                  height: 170px !important;
                  display: block;
                }
                .tag-url {
                  font-size: 9px;
                  font-family: monospace;
                  color: #64748b;
                  word-break: break-all;
                  margin: 0 0 10px 0;
                  line-height: 1.2;
                }
                .tag-footer {
                  font-size: 11px;
                  font-weight: 600;
                  color: #2563eb;
                  border-top: 1px solid #e2e8f0;
                  padding-top: 6px;
                }
              </style>
            </head>
            <body>
              <div class="tag-card">
                <div class="tag-title">${title}</div>
                <div class="tag-sub">${subtitle}</div>
                <div class="qr-box">${qrSvg}</div>
                <div class="tag-url">${targetUrl}</div>
                <div class="tag-footer">Task Manager • Home Assistant</div>
              </div>
            </body>
          </html>
        `);
        frameDoc.close();

        setTimeout(() => {
          try {
            frame.contentWindow.focus();
            frame.contentWindow.print();
          } catch (e) {
            console.error("Frame print failed", e);
          } finally {
            setTimeout(() => {
              try { frame.remove(); } catch (err) {}
            }, 3000);
          }
        }, 350);
      } catch (err) {
        console.error("Failed to create print frame", err);
      }
    }

    _getQrTargetUrl(item, itemType = "task") {
      const origin = window.location.origin;
      let basePath = window.location.pathname || "/task-manager";
      if (!basePath.endsWith("task-manager") && !basePath.endsWith("task-manager/")) {
        basePath = "/task-manager";
      }
      if (basePath.endsWith("/")) {
        basePath = basePath.slice(0, -1);
      }
      return itemType === "thing"
        ? `${origin}${basePath}?thing_id=${item.id}`
        : `${origin}${basePath}?action=complete&task_id=${item.id}`;
    }

    async _handleUrlParameters() {
      if (this._urlParamsHandled) return;
      if (!this._data || !this._data.tasks || this._data.tasks.length === 0) return;

      const getParam = (name) => {
        let val = null;
        try {
          val = new URLSearchParams(window.location.search).get(name);
        } catch (e) {}
        if (!val && window.location.hash && window.location.hash.includes("?")) {
          try {
            val = new URLSearchParams(window.location.hash.slice(window.location.hash.indexOf("?"))).get(name);
          } catch (e) {}
        }
        if (!val && window.location.href && window.location.href.includes("?")) {
          try {
            const queryPart = window.location.href.slice(window.location.href.indexOf("?")).split("#")[0];
            val = new URLSearchParams(queryPart).get(name);
          } catch (e) {}
        }
        return val;
      };

      const taskId = getParam("task_id") || getParam("complete_task") || getParam("taskId");
      const thingId = getParam("thing_id") || getParam("thingId");
      const action = getParam("action");

      if (!taskId && !thingId) return;
      this._urlParamsHandled = true;

      // Clean browser URL query string without reloading page
      try {
        const cleanUrl = window.location.pathname + (window.location.hash ? window.location.hash.split("?")[0] : "");
        window.history.replaceState({}, document.title, cleanUrl);
      } catch (e) {}

      if (taskId) {
        const task = this._data.tasks.find(t => t.id === taskId);
        if (task) {
          if (action === "view") {
            this.openTaskModal(task);
          } else {
            // Default action on task QR code is to complete the task
            if (task.status === "completed") {
              this._showToast(`ℹ️ ${this.t("taskAlreadyCompleted", { title: task.title })}`, "info");
            } else if (task.task_type === "reading") {
              this.openCompleteModal(task);
            } else {
              this._currentTab = "chores";
              this._filterStatus = "all";
              const isRecurring = Boolean(task.recurrence && task.recurrence.enabled);
              await this.completeTask(task.id);
              const updatedTask = (this._data.tasks || []).find(t => t.id === task.id) || task;
              if (isRecurring && updatedTask.due_date) {
                this._showToast(`🎉 ${this.t("recurringTaskCompletedViaQr", { title: task.title, nextDue: updatedTask.due_date })}`);
              } else {
                this._showToast(`🎉 ${this.t("taskCompletedViaQr", { title: task.title })}`);
              }
              setTimeout(() => {
                const el = this.shadowRoot && this.shadowRoot.querySelector(`[data-task-id="${task.id}"]`);
                if (el) {
                  el.scrollIntoView({ behavior: "smooth", block: "center" });
                }
              }, 250);
            }
          }
        } else {
          console.warn(`Task Manager: Task with ID ${taskId} not found for URL action.`);
          this._showToast(`⚠️ Aufgabe nicht gefunden (ID: ${taskId})`, "error");
        }
      } else if (thingId) {
        const thing = (this._data.things || []).find(th => th.id === thingId);
        if (thing) {
          this._currentTab = "things";
          this._render();
          this._showToast(`⚙️ ${this._escape(thing.name)}`, "info");
        }
      }
    }

    _getWarrantyStatus(thing) {
      if (!thing || !thing.warranty_expiry) return "none";
      try {
        const exp = new Date(thing.warranty_expiry.slice(0, 10));
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        const diffDays = Math.ceil((exp - now) / (1000 * 60 * 60 * 24));
        if (diffDays < 0) return "expired";
        if (diffDays <= 30) return "expiring_soon";
        return "valid";
      } catch (e) {
        return "none";
      }
    }

    openCompleteModal(task) {
      this._modalState = { type: "complete_details", task };
      this._render();
    }

    openQrModal(item, itemType) {
      this._modalState = { type: "qr_code", item, itemType };
      this._render();
    }

    openPartModal(part = null) {
      this._modalState = {
        type: "part",
        part: part || {
          name: "",
          part_number: "",
          thing_id: null,
          stock: 1,
          min_stock: 1,
          unit: "pcs",
          unit_price: 0.0,
          storage_location: "",
          reorder_url: "",
          notes: ""
        }
      };
      this._render();
    }

    async savePart(partData) {
      await this._callWS("task_manager/save_part", { part_data: partData });
      this.closeModal();
    }

    async deletePart(partId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_part", { part_id: partId });
      }
    }

    async adjustPartStock(partId, delta) {
      await this._callWS("task_manager/adjust_part_stock", { part_id: partId, delta: delta });
    }

    async skipTask(taskId) {
      if (confirm(this.t("skipConfirm"))) {
        await this._callWS("task_manager/skip_task", { task_id: taskId });
      }
    }

    async completeTask(taskId, details = null) {
      this._playSuccessSound();
      this._triggerConfetti();
      const payload = {
        task_id: taskId,
        user_id: this._activeUser
      };
      if (details) {
        if (details.reading_value !== undefined && details.reading_value !== null && details.reading_value !== "") {
          payload.reading_value = parseFloat(details.reading_value);
        }
        if (details.consumed_parts && details.consumed_parts.length > 0) {
          payload.consumed_parts = details.consumed_parts;
        }
        if (details.duration_minutes !== undefined && details.duration_minutes !== null && details.duration_minutes !== "") {
          payload.duration_minutes = parseInt(details.duration_minutes, 10);
        }
        if (details.cost !== undefined && details.cost !== null && details.cost !== "") {
          payload.cost = parseFloat(details.cost);
        }
        if (details.notes) {
          payload.notes = details.notes;
        }
        if (details.completed_at) {
          payload.completed_at = details.completed_at;
        }
      }
      const prevTask = (this._data.tasks || []).find(t => t.id === taskId);
      const isRecurring = Boolean(prevTask && prevTask.recurrence && prevTask.recurrence.enabled);

      await this._callWS("task_manager/complete_task", payload);
      this.closeModal();

      const updatedTask = (this._data.tasks || []).find(t => t.id === taskId);
      this._justCompletedTaskId = taskId;
      this._render();

      if (!this._urlParamsHandled) {
        if (updatedTask && isRecurring && updatedTask.due_date) {
          this._showToast(`🎉 ${this.t("recurringTaskCompleted", { title: updatedTask.title, nextDue: updatedTask.due_date })}`);
        } else if (updatedTask) {
          this._showToast(`🎉 ${this.t("taskCompleted", { title: updatedTask.title })}`);
        } else if (prevTask) {
          this._showToast(`🎉 ${this.t("taskCompleted", { title: prevTask.title })}`);
        }
      }

      setTimeout(() => {
        if (this._justCompletedTaskId === taskId) {
          this._justCompletedTaskId = null;
          this._render();
        }
      }, 5000);
    }

    async resetTask(taskId) {
      await this._callWS("task_manager/reset_task", { task_id: taskId });
    }

    async deleteTask(taskId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_task", { task_id: taskId });
      }
    }

    async duplicateTask(taskId) {
      await this._callWS("task_manager/duplicate_task", { task_id: taskId });
    }

    async pauseTask(taskId) {
      const task = (this._data.tasks || []).find(t => t.id === taskId);
      const res = await this._callWS("task_manager/pause_task", { task_id: taskId });
      if (res && res.success) {
        const title = task ? task.title : "";
        this._showToast(`⏸️ ${this.t("taskPaused", { title: title })}`);
      }
    }

    async resumeTask(taskId) {
      const task = (this._data.tasks || []).find(t => t.id === taskId);
      const res = await this._callWS("task_manager/resume_task", { task_id: taskId });
      if (res && res.success) {
        const title = task ? task.title : "";
        this._showToast(`▶️ ${this.t("taskResumed", { title: title })}`);
      }
    }

    async toggleSubtask(taskId, subtaskId, currentState) {
      await this._callWS("task_manager/update_subtask", {
        task_id: taskId,
        subtask_id: subtaskId,
        completed: !currentState
      });
    }

    async updateThingValue(thingId, delta = null, reset = false, value = null) {
      const payload = { thing_id: thingId, reset: Boolean(reset) };
      if (delta !== null && delta !== undefined) payload.delta = delta;
      if (value !== null && value !== undefined) payload.value = value;
      await this._callWS("task_manager/update_thing_value", payload);
    }

    async deleteThing(thingId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_thing", { thing_id: thingId });
      }
    }

    async deleteUser(userId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_user", { user_id: userId });
        if (this._activeUser === userId) {
          this._activeUser = this._data.users[0] ? this._data.users[0].id : null;
        }
      }
    }

    async deleteLabel(labelId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/delete_label", { label_id: labelId });
      }
    }

    _exportBackup() {
      const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this._data, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", jsonStr);
      downloadAnchor.setAttribute("download", `task_manager_backup_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }

    async _importBackup(fileInput) {
      const file = fileInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const parsed = JSON.parse(e.target.result);
          await this._callWS("task_manager/import_data", { data: parsed });
          alert(this.t("backupSuccess"));
        } catch (err) {
          alert(this.t("backupError") + ": " + err);
        }
      };
      reader.readAsText(file);
    }

    // Modal helpers
    openTaskModal(task = null) {
      this._modalState = { type: "task", task: task || this._getNewTaskTemplate() };
      this._render();
    }

    async openThingModal(thing = null) {
      this._modalState = { type: "thing", thing: thing || this._getNewThingTemplate() };
      this._availableNumericEntities = this._getNumericEntities();
      this._availableScriptEntities = this._getScriptEntities();
      this._render();

      try {
        const [numRes, scriptRes] = await Promise.all([
          this._hass ? this._hass.callWS({ type: "task_manager/get_ha_numeric_entities" }).catch(() => null) : Promise.resolve(null),
          this._hass ? this._hass.callWS({ type: "task_manager/get_ha_scripts" }).catch(() => null) : Promise.resolve(null)
        ]);
        if (numRes && Array.isArray(numRes.entities)) {
          const map = new Map();
          for (const ent of this._availableNumericEntities) map.set(ent.entity_id, ent);
          for (const ent of numRes.entities) map.set(ent.entity_id, ent);
          this._availableNumericEntities = Array.from(map.values()).sort((a, b) => (a.name || "").localeCompare(b.name || ""));
        }
        if (scriptRes && Array.isArray(scriptRes.scripts)) {
          const map = new Map();
          for (const ent of this._availableScriptEntities) map.set(ent.entity_id, ent);
          for (const ent of scriptRes.scripts) map.set(ent.entity_id, ent);
          this._availableScriptEntities = Array.from(map.values()).sort((a, b) => (a.name || "").localeCompare(b.name || ""));
        }
      } catch (err) {
        console.debug("Task Manager: Could not query backend entities", err);
      }
    }

    openUserModal(user = null) {
      this._modalState = { type: "user", user: user || this._getNewUserTemplate() };
      this._render();
    }

    openLabelModal(label = null) {
      this._modalState = { type: "label", label: label || this._getNewLabelTemplate() };
      this._render();
    }

    _getFrontendTodoEntities() {
      const list = [];
      if (this._hass && this._hass.states) {
        for (const [entityId, stateObj] of Object.entries(this._hass.states)) {
          if (entityId.startsWith("todo.") && !entityId.startsWith("todo.task_manager")) {
            const friendlyName = (stateObj && stateObj.attributes && stateObj.attributes.friendly_name) || entityId;
            let icon = (stateObj && stateObj.attributes && stateObj.attributes.icon) || "mdi:format-list-checks";
            let providerType = "generic";
            let providerName = friendlyName;

            const lowerId = entityId.toLowerCase();
            if (lowerId.includes("google")) {
              providerType = "google_tasks";
              providerName = "Google Tasks";
              icon = "mdi:google";
            } else if (lowerId.includes("todoist")) {
              providerType = "todoist";
              providerName = "Todoist";
              icon = "mdi:checkbox-marked";
            } else if (lowerId.includes("bring")) {
              providerType = "bring";
              providerName = "Bring Shopping";
              icon = "mdi:cart";
            } else if (lowerId.includes("caldav") || lowerId.includes("nextcloud")) {
              providerType = "caldav";
              providerName = "CalDAV";
              icon = "mdi:calendar-sync";
            } else if (lowerId.includes("local")) {
              providerType = "local_todo";
              providerName = "Local To-do";
              icon = "mdi:clipboard-list";
            } else if (lowerId.includes("shopping") || lowerId.includes("einkauf")) {
              providerType = "shopping_list";
              providerName = "Shopping List";
              icon = "mdi:cart-outline";
            }

            list.push({
              entity_id: entityId,
              name: friendlyName,
              provider_name: providerName,
              provider_type: providerType,
              icon: icon
            });
          }
        }
      }
      return list;
    }

    _getNumericEntities() {
      const list = [];
      if (this._hass && this._hass.states) {
        for (const [entityId, stateObj] of Object.entries(this._hass.states)) {
          if (entityId.startsWith("task_manager") || entityId.startsWith("sensor.task_manager")) continue;
          const s = stateObj ? stateObj.state : "";
          const isNum = !isNaN(parseFloat(s)) ||
            (stateObj && stateObj.attributes && Boolean(stateObj.attributes.unit_of_measurement)) ||
            entityId.startsWith("input_number.") ||
            entityId.startsWith("number.") ||
            entityId.startsWith("counter.");
          if (isNum) {
            const name = (stateObj.attributes && stateObj.attributes.friendly_name) || entityId;
            const unit = (stateObj.attributes && stateObj.attributes.unit_of_measurement) || "";
            list.push({ entity_id: entityId, name, state: s, unit });
          }
        }
      }
      list.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
      return list;
    }

    _getScriptEntities() {
      const list = [];
      if (this._hass && this._hass.states) {
        for (const [entityId, stateObj] of Object.entries(this._hass.states)) {
          if (entityId.startsWith("script.")) {
            const name = (stateObj.attributes && stateObj.attributes.friendly_name) || entityId;
            list.push({ entity_id: entityId, name });
          }
        }
      }
      list.sort((a, b) => a.name.localeCompare(b.name));
      return list;
    }

    async openLinkProviderModal() {
      const localEntities = this._getFrontendTodoEntities();
      this._availableTodoEntities = localEntities;
      this._loadingTodoEntities = true;
      this._modalState = { type: "link_provider", manualMode: false };
      this._render();

      try {
        const res = await this._hass.callWS({ type: "task_manager/get_ha_todo_entities" });
        if (res && Array.isArray(res.entities)) {
          const map = new Map();
          for (const ent of localEntities) {
            map.set(ent.entity_id, ent);
          }
          for (const ent of res.entities) {
            map.set(ent.entity_id, ent);
          }
          this._availableTodoEntities = Array.from(map.values());
        }
      } catch (err) {
        console.warn("Task Manager: Could not query backend todo entities, using frontend states", err);
      } finally {
        this._loadingTodoEntities = false;
        if (this._modalState && this._modalState.type === "link_provider") {
          this._render();
        }
      }
    }

    async linkProvider(entityId, name = "") {
      if (!entityId) return;
      const ent = (this._availableTodoEntities || []).find(e => e.entity_id === entityId);
      const providerType = ent ? ent.provider_type : "generic";
      const icon = ent ? ent.icon : "mdi:format-list-checks";
      const displayName = name.trim() || (ent ? ent.name : entityId);

      await this._callWS("task_manager/link_provider", {
        entity_id: entityId,
        name: displayName,
        provider_type: providerType,
        icon: icon
      });
      this.closeModal();
    }

    async unlinkProvider(entityId) {
      if (confirm(this.t("confirmDelete"))) {
        await this._callWS("task_manager/unlink_provider", { entity_id: entityId });
      }
    }

    async syncProviders() {
      await this._callWS("task_manager/sync_providers");
      this._playSuccessSound();
      alert(this.t("syncSuccess"));
    }

    closeModal() {
      this._modalState = null;
      this._render();
    }

    _getNewTaskTemplate() {
      const today = new Date().toISOString().slice(0, 10);
      return {
        id: "",
        title: "",
        description: "",
        due_date: today,
        due_time: "",
        priority: "none",
        assignees: this._activeUser ? [this._activeUser] : [],
        current_assignee: this._activeUser || "",
        rotation_mode: "none",
        labels: [],
        recurrence: {
          enabled: false,
          type: "none",
          interval: 1,
          days_of_week: [],
          based_on: "due_date"
        },
        subtasks: [],
        points: this._data.settings.default_points || 10,
        linked_thing_id: "",
        thing_action: "reset"
      };
    }

    _getNewThingTemplate() {
      return {
        id: "",
        name: "",
        category: "General",
        icon: "mdi:chart-arc",
        current_value: 0,
        target_value: 0,
        threshold_operator: ">=",
        external_entity_id: "",
        script_entity_id: "",
        initial_value: 0,
        unit: "",
        auto_task_creation: false,
        auto_task_title: ""
      };
    }

    _getNewUserTemplate() {
      return {
        id: "",
        name: "",
        color: "#3b82f6",
        avatar: "mdi:account",
        points: 0,
        streak: 0
      };
    }

    _getNewLabelTemplate() {
      return {
        id: "",
        name: "",
        color: "#10b981",
        icon: "mdi:tag"
      };
    }

    _getFilteredTasks() {
      let tasks = [...this._data.tasks];
      const todayStr = new Date().toISOString().slice(0, 10);

      // Search filter
      if (this._searchQuery.trim()) {
        const q = this._searchQuery.toLowerCase();
        tasks = tasks.filter(t => 
          (t.title && t.title.toLowerCase().includes(q)) || 
          (t.description && t.description.toLowerCase().includes(q)) ||
          (t.tags && t.tags.some(tag => String(tag).toLowerCase().includes(q)))
        );
      }

      // Status filter
      if (this._filterStatus === "inactive") {
        tasks = tasks.filter(t => t.is_active === false);
      } else if (this._filterStatus === "today") {
        tasks = tasks.filter(t => t.is_active !== false && t.status === "pending" && t.due_date === todayStr);
      } else if (this._filterStatus === "due_soon") {
        tasks = tasks.filter(t => {
          if (t.is_active === false || t.status !== "pending" || !t.due_date) return false;
          const dsDays = (t.due_soon_days !== undefined && t.due_soon_days > 0) ? t.due_soon_days : 7;
          const soonDate = new Date();
          soonDate.setDate(soonDate.getDate() + dsDays);
          const soonStr = soonDate.toISOString().slice(0, 10);
          return t.due_date <= soonStr;
        });
      } else if (this._filterStatus === "upcoming") {
        tasks = tasks.filter(t => t.is_active !== false && t.status === "pending" && t.due_date > todayStr && t.due_date < "2099-01-01");
      } else if (this._filterStatus === "overdue") {
        tasks = tasks.filter(t => t.is_active !== false && t.status === "pending" && t.due_date && t.due_date < todayStr);
      } else if (this._filterStatus === "completed") {
        tasks = tasks.filter(t => t.status === "completed");
      } else {
        // 'all' shows all pending tasks (including paused)
        tasks = tasks.filter(t => t.status === "pending");
      }

      // Assignee filter
      if (this._filterAssignee !== "all") {
        tasks = tasks.filter(t => t.current_assignee === this._filterAssignee || (t.assignees && t.assignees.includes(this._filterAssignee)));
      }

      // Label filter
      if (this._filterLabel !== "all") {
        tasks = tasks.filter(t => t.labels && t.labels.includes(this._filterLabel));
      }

      // Priority filter
      if (this._filterPriority !== "all") {
        tasks = tasks.filter(t => t.priority === this._filterPriority);
      }

      // Provider / List filter
      if (this._filterProvider === "task_manager") {
        tasks = tasks.filter(t => !t.is_external);
      } else if (this._filterProvider && this._filterProvider !== "all") {
        tasks = tasks.filter(t => t.provider_entity_id === this._filterProvider);
      }

      // Sort: overdue first, then by due date, then priority
      tasks.sort((a, b) => {
        const pOrder = { p1: 1, p2: 2, p3: 3, p4: 4, none: 5 };
        if (a.due_date !== b.due_date) {
          return (a.due_date || "") < (b.due_date || "") ? -1 : 1;
        }
        return (pOrder[a.priority] || 5) - (pOrder[b.priority] || 5);
      });

      return tasks;
    }

    _render() {
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;
      if (!isGamification && this._currentTab === "leaderboard") {
        this._currentTab = "chores";
      }

      const todayStr = new Date().toISOString().slice(0, 10);
      const pendingCount = this._data.tasks.filter(t => t.status === "pending").length;
      const todayCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date === todayStr).length;
      const overdueCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;

      this.shadowRoot.innerHTML = `
        <style>
          :host {
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
            background-color: var(--primary-background-color, #f8fafc);
            color: var(--primary-text-color, #0f172a);
            color-scheme: light dark;
            font-family: var(--paper-font-body1_-_font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
            box-sizing: border-box;
            overflow: hidden;
            position: relative;
            accent-color: var(--primary-color, #2563eb);
          }

          * {
            box-sizing: border-box;
          }

          /* Header bar */
          .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 24px;
            background: var(--card-background-color, #ffffff);
            border-bottom: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            flex-shrink: 0;
            gap: 16px;
          }

          .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
          }

          .menu-btn {
            background: var(--card-background-color, #ffffff);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
            color: var(--primary-text-color, inherit);
            width: 38px;
            height: 38px;
            min-width: 38px;
            border-radius: 10px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.15s ease;
            padding: 0;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
          }

          .menu-btn:hover {
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
            border-color: var(--primary-color, #2563eb);
            color: var(--primary-color, #2563eb);
            transform: translateY(-1px);
          }

          .menu-btn:active {
            transform: translateY(0);
          }

          .menu-btn svg {
            display: block;
            pointer-events: none;
          }

          @media (max-width: 870px) {
            .menu-btn {
              display: inline-flex !important;
            }
          }

          .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            color: inherit;
          }

          .brand-logo {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: var(--primary-color, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-primary-color, #ffffff);
            font-weight: 700;
            font-size: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
          }

          .brand-title {
            font-size: 19px;
            font-weight: 700;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--primary-text-color, inherit);
          }

          .status-badge {
            font-size: 12px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 9999px;
            background: rgba(37, 99, 235, 0.15);
            color: var(--primary-color, #2563eb);
            border: 1px solid rgba(37, 99, 235, 0.25);
          }

          .header-actions {
            display: flex;
            align-items: center;
            gap: 12px;
          }

          .user-select {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
          }

          .user-select option {
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
          }

          .user-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
          }

          .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
          }

          .btn-primary {
            background: var(--primary-color, #2563eb);
            color: var(--text-primary-color, #ffffff);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
          }

          .btn-primary:hover {
            filter: brightness(1.1);
            transform: translateY(-1px);
          }

          .btn-secondary {
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
            color: var(--primary-text-color, inherit);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
          }

          .btn-secondary:hover {
            background: var(--divider-color, rgba(127, 127, 127, 0.2));
          }

          /* Tab navigation */
          .nav-tabs {
            display: flex;
            gap: 6px;
            padding: 10px 24px;
            background: var(--card-background-color, #ffffff);
            border-bottom: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            overflow-x: auto;
          }

          .nav-tab {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            color: var(--secondary-text-color, #64748b);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            white-space: nowrap;
          }

          .nav-tab:hover {
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.1));
            color: var(--primary-text-color, inherit);
          }

          .nav-tab.active {
            background: rgba(37, 99, 235, 0.15);
            color: var(--primary-color, #2563eb);
          }

          .badge-pill {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 999px;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
            color: var(--secondary-text-color, inherit);
          }

          .nav-tab.active .badge-pill {
            background: var(--primary-color, #2563eb);
            color: var(--text-primary-color, #ffffff);
          }

          /* Main body */
          .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px 24px;
          }

          /* Filters toolbar */
          .toolbar {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
          }

          .filter-pills {
            display: flex;
            gap: 6px;
            overflow-x: auto;
          }

          .filter-pill {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            background: var(--card-background-color, #ffffff);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.25)));
            color: var(--secondary-text-color, #64748b);
            cursor: pointer;
          }

          .filter-pill.active {
            background: var(--primary-color, #2563eb);
            color: var(--text-primary-color, #ffffff);
            border-color: var(--primary-color, #2563eb);
          }

          .filter-selects {
            display: flex;
            gap: 8px;
          }

          .select-input, .text-input {
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.3)));
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
            font-size: 13px;
            outline: none;
          }

          .select-input option {
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
          }

          .select-input:focus, .text-input:focus {
            border-color: var(--primary-color, #2563eb);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
          }

          /* Tasks list */
          .task-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 14px;
          }

          .task-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            position: relative;
            color: var(--primary-text-color, inherit);
          }

          .task-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
          }

          .task-card.priority-p1 { border-left: 5px solid var(--error-color, #ef4444); }
          .task-card.priority-p2 { border-left: 5px solid #f97316; }
          .task-card.priority-p3 { border-left: 5px solid var(--primary-color, #3b82f6); }
          .task-card.priority-p4 { border-left: 5px solid var(--divider-color, #94a3b8); }
          .task-card.completed-task { opacity: 0.65; }
          .task-card.is-paused {
            opacity: 0.78;
            border-style: dashed;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.04));
          }

          .task-top {
            display: flex;
            align-items: flex-start;
            gap: 12px;
          }

          .check-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.4)));
            background: transparent;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            color: transparent;
            transition: all 0.2s ease;
            margin-top: 2px;
          }

          .check-btn:hover {
            border-color: var(--success-color, #10b981);
            background: rgba(16, 185, 129, 0.15);
            color: var(--success-color, #10b981);
          }

          .check-btn.checked,
          .completed-task .check-btn {
            background: var(--success-color, #10b981) !important;
            border-color: var(--success-color, #10b981) !important;
            color: #ffffff !important;
          }

          .task-card.just-completed {
            border: 2px solid #10b981 !important;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.45) !important;
            animation: card-just-completed-pulse 2s ease-in-out infinite;
          }
          @keyframes card-just-completed-pulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
            50% { transform: scale(1.015); box-shadow: 0 0 25px rgba(16, 185, 129, 0.6); }
          }

          .task-info {
            flex: 1;
            min-width: 0;
          }

          .task-title {
            font-size: 15px;
            font-weight: 600;
            line-height: 1.3;
            margin: 0 0 4px 0;
            word-break: break-word;
            color: var(--primary-text-color, inherit);
          }

          .completed-task .task-title {
            text-decoration: line-through;
            color: var(--disabled-text-color, #94a3b8);
          }

          .task-desc {
            font-size: 13px;
            color: var(--secondary-text-color, #64748b);
            margin: 0;
            line-height: 1.4;
          }

          .task-meta {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
            margin-top: 4px;
          }

          .meta-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.12));
            color: var(--secondary-text-color, inherit);
          }

          .meta-chip.overdue { background: rgba(239, 68, 68, 0.15); color: var(--error-color, #ef4444); }
          .meta-chip.due-today { background: rgba(245, 158, 11, 0.15); color: var(--warning-color, #f59e0b); }
          .meta-chip.priority-p1 { background: rgba(239, 68, 68, 0.15); color: var(--error-color, #ef4444); }
          .meta-chip.priority-p2 { background: rgba(249, 115, 22, 0.15); color: #f97316; }
          .meta-chip.priority-p3 { background: rgba(59, 130, 246, 0.15); color: var(--primary-color, #3b82f6); }
          .meta-chip.chip-points { background: rgba(245, 158, 11, 0.15); color: #d97706; }

          /* Subtasks checklist */
          .subtasks-box {
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
            border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.12));
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 4px;
          }

          .subtask-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            padding: 3px 0;
            color: var(--primary-text-color, inherit);
          }

          .subtask-item input {
            cursor: pointer;
          }

          .subtask-title.done {
            text-decoration: line-through;
            color: var(--disabled-text-color, #94a3b8);
          }

          .task-bottom {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.12));
            padding-top: 8px;
            margin-top: 4px;
          }

          .assignee-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 500;
            color: var(--primary-text-color, inherit);
          }

          
          /* Parts Shelf & Warranty Styles */
          .parts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
          }

          .part-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
          }

          .warranty-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
          }
          .warranty-badge.valid {
            background: rgba(16, 185, 129, 0.15);
            color: var(--success-color, #10b981);
          }
          .warranty-badge.expiring_soon {
            background: rgba(245, 158, 11, 0.15);
            color: var(--warning-color, #f59e0b);
          }
          .warranty-badge.expired {
            background: rgba(239, 68, 68, 0.15);
            color: var(--error-color, #ef4444);
          }

          /* Things grid */
          .things-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
          }

          .thing-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            color: var(--primary-text-color, inherit);
          }

          .thing-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
          }

          .thing-title-group {
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .thing-icon {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: rgba(37, 99, 235, 0.12);
            color: var(--primary-color, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
          }

          .progress-bar-bg {
            width: 100%;
            height: 10px;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.2));
            border-radius: 999px;
            overflow: hidden;
            margin: 6px 0;
          }

          .progress-bar-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease;
          }

          .fill-green { background: var(--success-color, #10b981); }
          .fill-amber { background: var(--warning-color, #f59e0b); }
          .fill-red { background: var(--error-color, #ef4444); }

          .thing-actions {
            display: flex;
            gap: 8px;
          }

          /* Leaderboard */
          .leaderboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
          }

          .leaderboard-card {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            padding: 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            color: var(--primary-text-color, inherit);
          }

          .rank-badge {
            font-size: 24px;
          }

          .points-huge {
            font-size: 32px;
            font-weight: 800;
            color: var(--primary-color, #2563eb);
            margin: 4px 0;
          }

          /* Activity log */
          .activity-timeline {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            padding: 16px;
            color: var(--primary-text-color, inherit);
          }

          .activity-row {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.12));
            font-size: 13px;
          }

          /* Calendar View */
          .calendar-box {
            background: var(--card-background-color, #ffffff);
            border-radius: 14px;
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            color: var(--primary-text-color, inherit);
          }

          .calendar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
          }

          .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
          }

          .cal-day-header {
            text-align: center;
            font-size: 12px;
            font-weight: 700;
            color: var(--secondary-text-color, #64748b);
            padding: 6px 0;
          }

          .cal-cell {
            min-height: 80px;
            background: var(--card-background-color, #ffffff);
            border-radius: 8px;
            padding: 6px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 4px;
            border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.15));
            color: var(--primary-text-color, inherit);
          }

          .cal-cell:hover {
            border-color: var(--primary-color, #2563eb);
          }

          .cal-cell.today {
            background: rgba(37, 99, 235, 0.1);
            border-color: var(--primary-color, #3b82f6);
          }

          .cal-cell.selected {
            border-color: var(--primary-color, #2563eb);
            box-shadow: 0 0 0 2px var(--primary-color, #2563eb);
          }

          .cal-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
          }

          /* Modal dialog */
          .modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 16px;
          }

          .modal-close-btn {
            position: absolute;
            top: 14px;
            right: 14px;
            background: none;
            border: none;
            font-size: 18px;
            color: var(--secondary-text-color, #64748b);
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
            line-height: 1;
            z-index: 10;
          }
          .modal-close-btn:hover {
            background: rgba(127, 127, 127, 0.15);
            color: var(--primary-text-color, inherit);
          }

          .modal-window {
            position: relative;
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.2)));
            border-radius: 16px;
            max-width: 580px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
          }

          .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
          }

          .form-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--secondary-text-color, #475569);
          }

          /* Entity Combobox / Dropdown */
          .entity-picker-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            width: 100%;
          }

          .entity-picker-input {
            width: 100%;
            padding-right: 32px !important;
          }

          .entity-picker-clear-btn {
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: none;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.2));
            color: var(--secondary-text-color, #64748b);
            font-size: 11px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            transition: all 0.15s ease;
            z-index: 2;
          }

          .entity-picker-clear-btn:hover {
            background: var(--error-color, #ef4444);
            color: #ffffff;
          }

          .entity-dropdown-list {
            position: absolute;
            top: calc(100% + 4px);
            left: 0;
            right: 0;
            max-height: 220px;
            overflow-y: auto;
            background: var(--card-background-color, #ffffff);
            color: var(--primary-text-color, inherit);
            border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.3)));
            border-radius: 8px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
            z-index: 1050;
          }

          .entity-dropdown-item {
            padding: 8px 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.12));
            transition: background 0.1s ease;
          }

          .entity-dropdown-item:last-child {
            border-bottom: none;
          }

          .entity-dropdown-item:hover, .entity-dropdown-item.selected {
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
          }

          .entity-dropdown-name {
            font-weight: 600;
            font-size: 13px;
            color: var(--primary-text-color, inherit);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .entity-dropdown-id {
            font-size: 11px;
            color: var(--secondary-text-color, #64748b);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .entity-dropdown-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 6px;
            background: var(--secondary-background-color, rgba(127, 127, 127, 0.15));
            color: var(--secondary-text-color, inherit);
            white-space: nowrap;
            flex-shrink: 0;
          }

          .entity-dropdown-empty {
            padding: 12px;
            text-align: center;
            font-size: 12px;
            color: var(--secondary-text-color, #64748b);
          }

          .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 12px;
          }

          /* Confetti canvas */
          #confetti-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
          }

          /* Tablet Kiosk mount mode */
          :host(.tablet-mode) .header {
            padding: 18px 30px;
          }
          :host(.tablet-mode) .brand-title {
            font-size: 24px;
          }
          :host(.tablet-mode) .btn {
            padding: 12px 22px;
            font-size: 16px;
          }
          :host(.tablet-mode) .task-card {
            padding: 20px;
          }
          :host(.tablet-mode) .check-btn {
            width: 36px;
            height: 36px;
          }

          /* Floating Action Button (FAB) for Mobile */
          .mobile-fab {
            display: none;
            position: fixed;
            bottom: 24px;
            right: 20px;
            width: 56px;
            height: 56px;
            border-radius: 28px;
            background: var(--primary-color, #2563eb);
            color: var(--text-primary-color, #ffffff);
            border: none;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.28);
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 999;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            outline: none;
            -webkit-tap-highlight-color: transparent;
          }

          .mobile-fab:active {
            transform: scale(0.92);
          }

          /* Two-column responsive form grid */
          .form-grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
          }

          /* Modal Bottom-Sheet Handle for Mobile */
          .modal-handle {
            display: none;
            width: 40px;
            height: 4px;
            background: var(--ha-card-border-color, var(--divider-color, rgba(127, 127, 127, 0.4)));
            border-radius: 2px;
            margin: -4px auto 12px auto;
          }

          .btn-text-short {
            display: none;
          }

          /* Responsive & Mobile Phone (9:16 portrait) Optimizations */
          @media (max-width: 768px) {
            .mobile-fab {
              display: flex;
            }

            .header {
              flex-wrap: wrap;
              padding: 10px 14px;
              gap: 8px;
            }

            .header-left {
              flex: 1 1 100%;
              width: 100%;
              gap: 10px;
            }

            .menu-btn {
              width: 36px;
              height: 36px;
              min-width: 36px;
              border-radius: 8px;
            }

            .brand {
              gap: 10px;
              min-width: 0;
              flex: 1;
            }

            .brand-logo {
              width: 32px;
              height: 32px;
              min-width: 32px;
              font-size: 16px;
              border-radius: 8px;
            }

            .brand-title {
              font-size: 18px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
              display: flex;
              align-items: center;
              gap: 8px;
            }

            .status-badge {
              display: inline-block !important;
              font-size: 11px;
              padding: 2px 7px;
              white-space: nowrap;
            }

            .header-actions {
              flex: 1 1 100%;
              width: 100%;
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 8px;
              margin-top: 2px;
            }

            #btn-toggle-mount {
              display: none !important;
            }

            .user-select {
              flex: 1 1 auto;
              min-width: 0;
              max-width: none;
              padding: 7px 10px;
              font-size: 13px;
              text-overflow: ellipsis;
            }

            #btn-add-task {
              flex-shrink: 0;
              padding: 7px 14px;
              font-size: 13px;
              font-weight: 700;
              border-radius: 8px;
              white-space: nowrap;
            }

            .btn-text-full {
              display: inline !important;
            }

            .btn-text-short {
              display: none !important;
            }

            .nav-tabs {
              padding: 6px 10px;
              gap: 4px;
              scrollbar-width: none;
              -webkit-overflow-scrolling: touch;
            }

            .nav-tabs::-webkit-scrollbar {
              display: none;
            }

            .nav-tab {
              padding: 6px 10px;
              font-size: 13px;
              border-radius: 8px;
            }

            .badge-pill {
              font-size: 10px;
              padding: 1px 5px;
            }

            .content-area {
              padding: 12px 10px;
              padding-bottom: 90px;
            }

            .toolbar {
              flex-direction: column;
              align-items: stretch;
              gap: 10px;
              margin-bottom: 12px;
            }

            .filter-pills {
              padding-bottom: 2px;
              scrollbar-width: none;
              -webkit-overflow-scrolling: touch;
            }

            .filter-pills::-webkit-scrollbar {
              display: none;
            }

            .filter-pill {
              padding: 6px 12px;
              font-size: 12px;
              white-space: nowrap;
              flex-shrink: 0;
            }

            .filter-selects {
              display: grid;
              grid-template-columns: repeat(3, 1fr);
              gap: 6px;
            }

            #search-input {
              grid-column: 1 / -1;
              width: 100%;
              font-size: 16px;
              padding: 8px 12px;
            }

            .filter-selects .select-input {
              width: 100%;
              min-width: 0;
              padding: 6px 4px;
              font-size: 11px;
            }

            .task-grid {
              grid-template-columns: 1fr;
              gap: 10px;
            }

            .task-card {
              padding: 14px;
              border-radius: 12px;
              gap: 10px;
            }

            .check-btn {
              width: 32px;
              height: 32px;
              font-size: 14px;
            }

            .task-title {
              font-size: 14px;
            }

            .meta-chip {
              font-size: 10.5px;
              padding: 2px 6px;
            }

            .things-grid {
              grid-template-columns: 1fr;
              gap: 12px;
            }

            .thing-card {
              padding: 14px;
              border-radius: 12px;
            }

            .thing-actions .btn {
              padding: 8px;
              font-size: 12px;
            }

            .calendar-box {
              padding: 12px 6px;
              border-radius: 12px;
            }

            .calendar-header h2 {
              font-size: 15px !important;
            }

            .calendar-header .btn {
              padding: 5px 8px;
              font-size: 12px;
            }

            .calendar-grid {
              gap: 2px;
            }

            .cal-day-header {
              font-size: 10px;
              padding: 3px 0;
            }

            .cal-cell {
              min-height: 48px;
              padding: 3px 2px;
              border-radius: 6px;
            }

            .cal-cell div {
              font-size: 10px;
            }

            .leaderboard-cards {
              grid-template-columns: 1fr;
              gap: 10px;
              margin-bottom: 16px;
            }

            .leaderboard-card {
              padding: 14px;
              border-radius: 12px;
            }

            .points-huge {
              font-size: 26px;
            }

            .activity-timeline {
              padding: 12px;
              border-radius: 12px;
            }

            .provider-row {
              flex-direction: column;
              align-items: stretch !important;
              gap: 10px;
            }

            .provider-row .btn {
              align-self: flex-end;
            }

            .modal-backdrop {
              padding: 0;
              align-items: flex-end;
            }

            .modal-window {
              border-radius: 20px 20px 0 0;
              max-height: 94vh;
              padding: 18px 16px;
              padding-bottom: max(20px, env(safe-area-inset-bottom, 20px));
              gap: 12px;
              width: 100%;
              max-width: 100%;
            }

            .modal-handle {
              display: block;
            }

            .form-grid-2 {
              grid-template-columns: 1fr !important;
              gap: 10px !important;
            }

            .modal-window .text-input,
            .modal-window .select-input {
              font-size: 16px;
            }

            .modal-footer {
              display: flex;
              gap: 8px;
              margin-top: 8px;
            }

            .modal-footer .btn {
              flex: 1;
              justify-content: center;
              padding: 10px 14px;
              font-size: 14px;
            }
          }

          @media (max-width: 380px) {
            .header {
              padding: 8px 10px;
            }
            .brand-title {
              font-size: 16px;
            }
            .status-badge {
              font-size: 10px;
              padding: 1px 5px;
            }
            .user-select {
              padding: 6px 8px;
              font-size: 12px;
            }
            #btn-add-task {
              padding: 6px 10px;
              font-size: 12px;
            }
          }
        </style>

        <canvas id="confetti-canvas"></canvas>

        <!-- Top Header -->
        <header class="header">
          <div class="header-left">
            <button class="menu-btn" id="menu-toggle-btn" aria-label="${this.t("menuToggle")}" title="${this.t("menuToggle")}">
              <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>
            <div class="brand">
              <div class="brand-logo">✓</div>
              <div class="brand-title">
                <span>${this.t("appName")}</span>
                <span class="status-badge">${this.t("openTasksCount", { count: pendingCount })}</span>
              </div>
            </div>
          </div>

          <div class="header-actions">
            <!-- Active user switcher -->
            ${this._renderUserSelector()}

            <!-- Tablet mode toggle -->
            <button class="btn btn-secondary" id="btn-toggle-mount">
              ${this._tabletMode ? "📱 " + this.t("exitMountMode") : "📺 " + this.t("mountMode")}
            </button>

            <!-- Add Task CTA -->
            <button class="btn btn-primary" id="btn-add-task">
              <span class="btn-text-full">${this._currentTab === "things" ? "+ " + this.t("addThing") : this._currentTab === "parts" ? "+ " + this.t("addPart") : "+ " + this.t("addTask")}</span>
              <span class="btn-text-short">+</span>
            </button>
          </div>
        </header>

        <!-- Tabs Bar -->
        <nav class="nav-tabs">
          <div class="nav-tab ${this._currentTab === "chores" ? "active" : ""}" data-tab="chores">
            📋 ${this.t("chores")} <span class="badge-pill">${pendingCount}</span>
          </div>
          <div class="nav-tab ${this._currentTab === "calendar" ? "active" : ""}" data-tab="calendar">
            📅 ${this.t("calendar")}
          </div>
          <div class="nav-tab ${this._currentTab === "things" ? "active" : ""}" data-tab="things">
            ⚙️ ${this.t("things")} <span class="badge-pill">${this._data.things.length}</span>
          </div>
          <div class="nav-tab ${this._currentTab === "parts" ? "active" : ""}" data-tab="parts">
            📦 ${this.t("parts")} <span class="badge-pill">${(this._data.parts || []).length}</span>
          </div>
          ${isGamification ? `
            <div class="nav-tab ${this._currentTab === "leaderboard" ? "active" : ""}" data-tab="leaderboard">
              🏆 ${this.t("leaderboard")}
            </div>
          ` : ""}
          <div class="nav-tab ${this._currentTab === "settings" ? "active" : ""}" data-tab="settings">
            🛠️ ${this.t("settings")}
          </div>
        </nav>

        <!-- Content Area -->
        <main class="content-area">
          ${this._renderTabContent()}
        </main>

        <!-- Floating Action Button for Mobile (Always accessible in 9:16 portrait) -->
        ${!this._modalState ? `
        <button class="mobile-fab" id="fab-add-btn" aria-label="${this._currentTab === "things" ? this.t("addThing") : this._currentTab === "parts" ? this.t("addPart") : this.t("addTask")}" title="${this._currentTab === "things" ? this.t("addThing") : this._currentTab === "parts" ? this.t("addPart") : this.t("addTask")}">
          <svg viewBox="0 0 24 24" width="26" height="26" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        ` : ""}

        <!-- Modals -->
        ${this._renderModal()}
      `;

      this._attachEventListeners();
      this._updateSidebarVisibility();
    }

    _renderUserSelector() {
      if (!this._data.users || this._data.users.length === 0) return "";
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;

      return `
        <select class="user-select" id="header-user-select" title="${this.t("activeMember")}">
          ${this._data.users.map(u => `
            <option value="${u.id}" ${u.id === this._activeUser ? "selected" : ""}>
              👤 ${this._escape(u.name)}${isGamification ? ` (${u.points || 0} ${this.t("pts")})` : ""}
            </option>
          `).join("")}
        </select>
      `;
    }

    _renderTabContent() {
      switch (this._currentTab) {
        case "chores":
          return this._renderChoresView();
        case "calendar":
          return this._renderCalendarView();
        case "things":
          return this._renderThingsView();
        case "parts":
          return this._renderPartsView();
        case "leaderboard":
          return this._renderLeaderboardView();
        case "settings":
          return this._renderSettingsView();
        default:
          return "";
      }
    }

    // ================= VIEW: CHORES =================
    _renderChoresView() {
      const tasks = this._getFilteredTasks();
      const todayStr = new Date().toISOString().slice(0, 10);
      const overdueCount = this._data.tasks.filter(t => t.status === "pending" && t.due_date && t.due_date < todayStr).length;
      const pausedCount = this._data.tasks.filter(t => t.is_active === false).length;

      return `
        <div class="toolbar">
          <div class="filter-pills">
            <button class="filter-pill ${this._filterStatus === "all" ? "active" : ""}" data-status="all">${this.t("all")}</button>
            <button class="filter-pill ${this._filterStatus === "today" ? "active" : ""}" data-status="today">🔥 ${this.t("today")}</button>
            <button class="filter-pill ${this._filterStatus === "due_soon" ? "active" : ""}" data-status="due_soon">⏳ ${this.t("dueSoon")}</button>
            <button class="filter-pill ${this._filterStatus === "upcoming" ? "active" : ""}" data-status="upcoming">${this.t("upcoming")}</button>
            <button class="filter-pill ${this._filterStatus === "overdue" ? "active" : ""}" data-status="overdue">
              ⚠️ ${this.t("overdue")} ${overdueCount > 0 ? `(${overdueCount})` : ""}
            </button>
            ${pausedCount > 0 ? `
              <button class="filter-pill ${this._filterStatus === "inactive" ? "active" : ""}" data-status="inactive">
                ⏸️ ${this.t("isPaused")} (${pausedCount})
              </button>
            ` : ""}
            <button class="filter-pill ${this._filterStatus === "completed" ? "active" : ""}" data-status="completed">✓ ${this.t("completed")}</button>
          </div>

          <div class="filter-selects">
            <input type="text" class="text-input" id="search-input" placeholder="${this.t("searchPlaceholder")}" value="${this._searchQuery}">

            <select class="select-input" id="filter-assignee">
              <option value="all">${this.t("assignee")}: ${this.t("all")}</option>
              ${this._data.users.map(u => `<option value="${u.id}" ${this._filterAssignee === u.id ? "selected" : ""}>${u.name}</option>`).join("")}
            </select>

            <select class="select-input" id="filter-label">
              <option value="all">${this.t("label")}: ${this.t("all")}</option>
              ${this._data.labels.map(l => `<option value="${l.id}" ${this._filterLabel === l.id ? "selected" : ""}>${l.name}</option>`).join("")}
            </select>

            <select class="select-input" id="filter-provider">
              <option value="all">${this.t("filterProvider")}: ${this.t("allLists")}</option>
              <option value="task_manager" ${this._filterProvider === "task_manager" ? "selected" : ""}>🏠 ${this.t("taskManagerList")}</option>
              ${(this._data.providers || []).map(p => `<option value="${p.entity_id}" ${this._filterProvider === p.entity_id ? "selected" : ""}>🔗 ${this._escape(p.name || p.entity_id)}</option>`).join("")}
            </select>
          </div>
        </div>

        ${tasks.length === 0 ? `
          <div style="text-align: center; padding: 48px 16px; color: var(--secondary-text-color, #64748b);">
            <div style="font-size: 44px; margin-bottom: 12px;">🎉</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 14px;">${this.t("noTasks")}</div>
            <button class="btn btn-primary" id="btn-empty-add-task">+ ${this.t("addTask")}</button>
          </div>
        ` : `
          <div class="task-grid">
            ${tasks.map(t => this._renderTaskCard(t, todayStr)).join("")}
          </div>
        `}
      `;
    }

    _renderTaskCard(task, todayStr) {
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;
      const isCompleted = task.status === "completed";
      const isOverdue = !isCompleted && task.due_date && task.due_date < todayStr;
      const isToday = !isCompleted && task.due_date === todayStr;
      const isJustCompleted = this._justCompletedTaskId === task.id;

      const assigneeUser = this._data.users.find(u => u.id === task.current_assignee);
      const linkedThing = task.linked_thing_id ? this._data.things.find(th => th.id === task.linked_thing_id) : null;

      const subtasks = task.subtasks || [];
      const completedSubtasks = subtasks.filter(st => st.completed).length;

      return `
        <div class="task-card priority-${task.priority} ${isCompleted ? "completed-task" : ""} ${isJustCompleted ? "just-completed" : ""} ${task.is_active === false ? "is-paused" : ""}" data-task-id="${task.id}">
          <div class="task-top">
            <button class="check-btn ${isJustCompleted ? "checked" : ""}" data-complete-task="${task.id}" title="${isCompleted ? this.t("reset") : this.t("done")}">
              ✓
            </button>
            <div class="task-info">
              <div class="task-title" style="display:flex; align-items:center; flex-wrap:wrap; gap:6px;">
                <span>${this._escape(task.title)}</span>
                ${isJustCompleted ? `
                  <span class="meta-chip chip-just-completed" style="background:#10b981; color:#ffffff; font-weight:700; font-size:11px; padding:2px 8px; border-radius:10px;">
                    ✓ ${this.t("justCompletedBadge", { nextDue: task.due_date || "" })}
                  </span>
                ` : ""}
              </div>
              ${task.description ? `<p class="task-desc">${this._escape(task.description)}</p>` : ""}

              <div class="task-meta">
                ${task.task_type === "reading" ? `
                  <span class="meta-chip" style="background:rgba(6, 182, 212, 0.15); color:#0891b2;">
                    📟 ${this.t("taskTypeReading")} ${task.last_reading_value !== undefined && task.last_reading_value !== null ? `(${task.last_reading_value} ${task.reading_unit || ""})` : ""}
                  </span>
                ` : ""}

                ${task.consumed_parts && task.consumed_parts.length ? `
                  <span class="meta-chip" style="background:rgba(249, 115, 22, 0.15); color:#ea580c;">
                    📦 ${task.consumed_parts.length} ${this.t("parts")}
                  </span>
                ` : ""}

                ${task.is_external ? `
                  <span class="meta-chip" style="background:var(--secondary-background-color, rgba(127,127,127,0.12)); color:var(--primary-text-color, inherit); border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); font-weight:600;">
                    🔗 ${this._escape(task.provider_name || this.t("externalTask"))}
                  </span>
                ` : ""}

                ${task.due_date ? `
                  <span class="meta-chip ${isOverdue ? "overdue" : isToday ? "due-today" : ""}">
                    ${task.due_date >= "2099-01-01" && linkedThing ? `⚡ ${this.t("waitingForThreshold")}` : `📅 ${task.due_date} ${task.due_time || ""}`}
                  </span>
                ` : ""}

                ${task.priority && task.priority !== "none" ? `
                  <span class="meta-chip priority-${task.priority}">
                    ${task.priority.toUpperCase()}
                  </span>
                ` : ""}

                ${task.recurrence && task.recurrence.enabled ? `
                  <span class="meta-chip">
                    🔄 ${this.t(task.recurrence.type)} ${task.recurrence.interval > 1 ? `(${task.recurrence.interval})` : ""}
                  </span>
                ` : ""}

                ${(isGamification && task.points) ? `
                  <span class="meta-chip chip-points" style="background: rgba(245, 158, 11, 0.15); color: #d97706;">
                    ⭐ +${task.points} ${this.t("pts")}
                  </span>
                ` : ""}

                ${linkedThing ? `
                  <span class="meta-chip" style="background: rgba(2, 132, 199, 0.15); color: #0284c7;">
                    ⚙️ ${this._escape(linkedThing.name)}
                  </span>
                ` : ""}

                ${task.is_active === false ? `
                  <span class="meta-chip" style="background:rgba(100,116,139,0.15); color:#64748b;">
                    ⏸️ ${this.t("isPaused")}
                  </span>
                ` : ""}

                ${task.times_completed > 0 ? `
                  <span class="meta-chip" style="background:rgba(16,185,129,0.12); color:#10b981;" title="${this.t("timesCompleted", { count: task.times_completed })}">
                    🔁 ${task.times_completed}x
                  </span>
                ` : ""}

                ${task.last_done_date ? `
                  <span class="meta-chip" style="background:rgba(16,185,129,0.12); color:#10b981;" title="${this.t("lastDoneDate")}: ${task.last_done_date}">
                    ✓ ${task.last_done_date === todayStr ? this.t("doneToday") : `${this.t("lastDoneDate")}: ${task.last_done_date}`}
                  </span>
                ` : ""}

                ${task.tags && task.tags.length ? task.tags.map(tg => `
                  <span class="meta-chip" style="background:rgba(139,92,246,0.12); color:#8b5cf6;">🏷️ ${this._escape(tg)}</span>
                `).join("") : ""}

                ${task.dependencies && task.dependencies.length ? `
                  <span class="meta-chip" style="background:rgba(234,179,8,0.15); color:#ca8a04;" title="${this.t("dependencies")}">
                    🔗 ${task.dependencies.length} ${this.t("dependencies")}
                  </span>
                ` : ""}

                ${task.labels && task.labels.map(lId => {
                  const lbl = this._data.labels.find(l => l.id === lId);
                  return lbl ? `<span class="meta-chip" style="background:${lbl.color}15; color:${lbl.color};">${this._escape(lbl.name)}</span>` : "";
                }).join("")}
              </div>
            </div>
          </div>

          ${subtasks.length > 0 ? `
            <div class="subtasks-box">
              <div style="font-size: 11px; font-weight: 700; color: var(--secondary-text-color, #64748b); margin-bottom: 4px; display:flex; justify-content:space-between;">
                <span>${this.t("subtasks")} (${completedSubtasks}/${subtasks.length})</span>
                ${task.recurrence && task.recurrence.enabled ? `<span>🔄 ${this.t("autoResets")}</span>` : ""}
              </div>
              ${subtasks.map(st => `
                <label class="subtask-item">
                  <input type="checkbox" data-subtask-task="${task.id}" data-subtask-id="${st.id}" ${st.completed ? "checked" : ""}>
                  <span class="subtask-title ${st.completed ? "done" : ""}">${this._escape(st.title)}</span>
                </label>
              `).join("")}
            </div>
          ` : ""}

          <div class="task-bottom">
            <div class="assignee-badge">
              ${assigneeUser ? `
                <div class="user-avatar" style="background:${assigneeUser.color}; width:20px; height:20px; font-size:10px;">
                  ${assigneeUser.name.slice(0, 1).toUpperCase()}
                </div>
                <span>${this._escape(assigneeUser.name)}</span>
                ${task.rotation_mode && task.rotation_mode !== "none" ? `<span title="${this.t("rotation")}: ${this.t(task.rotation_mode)}">🔄</span>` : ""}
              ` : `<span style="color:var(--secondary-text-color, #94a3b8);">${this.t("none")}</span>`}
            </div>

            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              ${!isCompleted ? `
                <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-skip-task="${task.id}" title="${this.t("skipTask")}">⏭️</button>
                <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-details-complete-task="${task.id}" title="${this.t("completeWithDetails")}">📝</button>
              ` : ""}
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-qr-task="${task.id}" title="${this.t("qrCode")}">📱</button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-toggle-active-task="${task.id}" title="${task.is_active === false ? this.t("resume") : this.t("pause")}">
                ${task.is_active === false ? "▶️" : "⏸️"}
              </button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-duplicate-task="${task.id}" title="${this.t("duplicate")}">📋</button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px;" data-edit-task="${task.id}" title="${this.t("edit")}">✏️</button>
              <button class="btn btn-secondary" style="padding:4px 8px; font-size:12px; color:var(--error-color, #ef4444);" data-delete-task="${task.id}" title="${this.t("delete")}">🗑️</button>
            </div>
          </div>
        </div>
      `;
    }

    // ================= VIEW: CALENDAR =================
    _renderCalendarView() {
      const year = this._calendarDate.getFullYear();
      const month = this._calendarDate.getMonth();
      const monthNames = this.t("months");
      const weekdays = this.t("weekdays");

      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);

      // Start day offset (Monday = 0)
      let startOffset = firstDay.getDay() - 1;
      if (startOffset < 0) startOffset = 6;

      const daysInMonth = lastDay.getDate();
      const todayStr = new Date().toISOString().slice(0, 10);

      // Build task map for this month
      const taskMap = {};
      this._data.tasks.forEach(t => {
        if (t.due_date && t.status === "pending") {
          taskMap[t.due_date] = taskMap[t.due_date] || [];
          taskMap[t.due_date].push(t);
        }
      });

      const dayCells = [];
      for (let i = 0; i < startOffset; i++) {
        dayCells.push(`<div class="cal-cell" style="opacity:0.3;"></div>`);
      }

      for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const dayTasks = taskMap[dateStr] || [];
        const isToday = dateStr === todayStr;
        const isSelected = dateStr === this._calendarSelectedDay;

        dayCells.push(`
          <div class="cal-cell ${isToday ? "today" : ""} ${isSelected ? "selected" : ""}" data-cal-date="${dateStr}">
            <div style="font-size:12px; font-weight:700;">${d}</div>
            <div style="display:flex; flex-direction:column; gap:2px;">
              ${dayTasks.slice(0, 3).map(t => `
                <div style="font-size:10px; padding:2px 4px; border-radius:3px; background:var(--primary-color-light, rgba(37, 99, 235, 0.15)); color:var(--primary-color, #2563eb); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                  ${this._escape(t.title)}
                </div>
              `).join("")}
              ${dayTasks.length > 3 ? `<div style="font-size:9px; color:var(--secondary-text-color, #64748b);">+${dayTasks.length - 3} ${this.t("more")}</div>` : ""}
            </div>
          </div>
        `);
      }

      return `
        <div class="calendar-box">
          <div class="calendar-header">
            <h2 style="margin:0; font-size:18px;">${monthNames[month]} ${year}</h2>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-secondary" id="cal-prev">◀</button>
              <button class="btn btn-secondary" id="cal-today">${this.t("today")}</button>
              <button class="btn btn-secondary" id="cal-next">▶</button>
            </div>
          </div>

          <div class="calendar-grid">
            ${weekdays.map(w => `<div class="cal-day-header">${w}</div>`).join("")}
            ${dayCells.join("")}
          </div>

          ${this._calendarSelectedDay ? `
            <div style="margin-top:20px; border-top:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding-top:16px;">
              <h3 style="margin:0 0 12px 0;">${this.t("choresDueOn")} ${this._calendarSelectedDay}:</h3>
              <div class="task-grid">
                ${(taskMap[this._calendarSelectedDay] || []).map(t => this._renderTaskCard(t, todayStr)).join("")}
                ${(taskMap[this._calendarSelectedDay] || []).length === 0 ? `<p style="color:var(--secondary-text-color, #64748b);">${this.t("noChoresDueOnDate")}</p>` : ""}
              </div>
            </div>
          ` : ""}
        </div>
      `;
    }

    // ================= VIEW: THINGS =================
    _renderThingsView() {
      return `
        <div class="view-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; gap:12px;">
          <div>
            <h2 style="margin:0 0 4px 0; font-size:20px;">${this.t("things")}</h2>
            <p style="margin:0; font-size:13px; color:var(--secondary-text-color, #64748b);">
              ${this.t("thingsSubtitle")}
            </p>
          </div>
          <button class="btn btn-primary" id="btn-add-thing" style="flex-shrink:0;">+ ${this.t("addThing")}</button>
        </div>

        ${this._data.things.length === 0 ? `
          <div style="text-align: center; padding: 48px 16px; color: var(--secondary-text-color, #64748b);">
            <div style="font-size: 44px; margin-bottom: 12px;">⚙️</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 14px;">${this.t("noThings")}</div>
            <button class="btn btn-primary" id="btn-empty-add-thing">+ ${this.t("addThing")}</button>
          </div>
        ` : `
          <div class="things-grid">
            ${this._data.things.map(th => this._renderThingCard(th)).join("")}
          </div>
        `}
      `;
    }

    _renderThingCard(thing) {
      const cur = parseFloat(thing.current_value) || 0;
      const target = thing.target_value !== undefined && !isNaN(parseFloat(thing.target_value)) ? parseFloat(thing.target_value) : 0;
      const operator = thing.threshold_operator || ">=";
      const isLte = operator === "<=";

      let isAlert = false;
      let isWarning = false;
      let pct = 0;

      if (isLte) {
        isAlert = cur <= target;
        isWarning = !isAlert && cur <= target + 15;
        pct = Math.min(100, Math.max(0, Math.round(cur)));
      } else {
        isAlert = cur >= target;
        isWarning = !isAlert && cur >= target * 0.75;
        pct = target > 0 ? Math.min(100, Math.max(0, Math.round((cur / target) * 100))) : 100;
      }

      let fillColor = "fill-green";
      let statusText = this.t("statusNormal");
      if (isAlert) {
        fillColor = "fill-red";
        statusText = this.t("statusAlert");
      } else if (isWarning) {
        fillColor = "fill-amber";
        statusText = this.t("statusWarning");
      }

      return `
        <div class="thing-card">
          <div class="thing-header">
            <div class="thing-title-group">
              <div class="thing-icon">⚙️</div>
              <div>
                <div style="font-weight:700; font-size:15px;">${this._escape(thing.name)}</div>
                <div style="font-size:12px; color:var(--secondary-text-color, #64748b);">${this._escape(thing.category || this.t("categoryGeneral"))}</div>
              </div>
            </div>
            <div style="display:flex; gap:4px;">
              ${thing.documentation_url ? `
                <a href="${this._escape(thing.documentation_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding:4px 6px; font-size:11px; text-decoration:none;" title="${this.t("viewManual")}">📖</a>
              ` : ""}
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px;" data-qr-thing="${thing.id}" title="${this.t("qrCode")}">📱</button>
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px;" data-edit-thing="${thing.id}" title="${this.t("edit")}">✏️</button>
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px; color:var(--error-color, #ef4444);" data-delete-thing="${thing.id}" title="${this.t("delete")}">🗑️</button>
            </div>
          </div>

          <!-- Warranty & Specs -->
          <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
            ${(() => {
              const wStatus = this._getWarrantyStatus(thing);
              if (wStatus === "valid") {
                return `<span class="warranty-badge valid">🛡️ ${this.t("warrantyValid")} (${thing.warranty_expiry})</span>`;
              } else if (wStatus === "expiring_soon") {
                return `<span class="warranty-badge expiring_soon">⚠️ ${this.t("warrantyExpiringSoon")} (${thing.warranty_expiry})</span>`;
              } else if (wStatus === "expired") {
                return `<span class="warranty-badge expired">❌ ${this.t("warrantyExpired")} (${thing.warranty_expiry})</span>`;
              }
              return "";
            })()}
            ${thing.manufacturer || thing.model ? `
              <span class="meta-chip" style="background:var(--secondary-background-color, rgba(127,127,127,0.1));">
                🏭 ${this._escape([thing.manufacturer, thing.model].filter(Boolean).join(" "))}
              </span>
            ` : ""}
            ${thing.serial_number ? `
              <span class="meta-chip" style="background:var(--secondary-background-color, rgba(127,127,127,0.1)); font-family:monospace; font-size:10px;">
                SN: ${this._escape(thing.serial_number)}
              </span>
            ` : ""}
            ${thing.installation_date ? `
              <span class="meta-chip" style="background:var(--secondary-background-color, rgba(127,127,127,0.1));">
                📅 ${this._escape(thing.installation_date)}
              </span>
            ` : ""}
          </div>

          <div>
            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600;">
              <span>${cur} ${this._escape(thing.unit || "")} <span style="font-size:11px; color:var(--secondary-text-color, #64748b); font-weight:normal;">(${operator} ${target})</span></span>
              <span>${pct}%</span>
            </div>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill ${fillColor}" style="width: ${pct}%;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--secondary-text-color, #64748b); margin-top:2px;">
              <span>${statusText}</span>
              ${thing.last_reset ? `<span>${this.t("lastReset")}: ${thing.last_reset.slice(0, 10)}</span>` : ""}
            </div>
            ${thing.external_entity_id ? `
              <div style="font-size:11px; color:#0284c7; margin-top:4px; display:flex; align-items:center; gap:4px; background:rgba(2, 132, 199, 0.12); padding:2px 6px; border-radius:4px;">
                <span>🔗</span>
                <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${this._escape(thing.external_entity_id)}">${this._escape(thing.external_entity_id)}</span>
              </div>
            ` : ""}
            ${thing.script_entity_id ? `
              <div style="font-size:11px; color:#a78bfa; margin-top:4px; display:flex; align-items:center; gap:4px; background:rgba(124, 58, 237, 0.12); padding:2px 6px; border-radius:4px;">
                <span>📜</span>
                <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${this._escape(thing.script_entity_id)}">${this._escape(thing.script_entity_id)}</span>
              </div>
            ` : ""}
          </div>

          <div class="thing-actions">
            <button class="btn btn-secondary" style="flex:1;" data-thing-delta="${thing.id}" data-delta="1">+1</button>
            <button class="btn btn-secondary" style="flex:1;" data-thing-delta="${thing.id}" data-delta="-1">-1</button>
            <button class="btn btn-primary" style="flex:1;" data-thing-reset="${thing.id}">↺ ${this.t("reset")}</button>
          </div>
        </div>
      `;
    }

    // ================= VIEW: PARTS =================
    _renderPartsView() {
      const parts = this._data.parts || [];
      const lowStockCount = parts.filter(p => parseFloat(p.stock || 0) <= parseFloat(p.min_stock !== undefined ? p.min_stock : 1)).length;

      return `
        <div class="view-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; gap:12px; flex-wrap:wrap;">
          <div>
            <div style="display:flex; align-items:center; gap:8px;">
              <h2 style="margin:0; font-size:20px;">📦 ${this.t("parts")}</h2>
              ${lowStockCount > 0 ? `
                <span class="badge-pill" style="background:rgba(239, 68, 68, 0.2); color:#ef4444; font-size:12px; padding:3px 8px;">
                  ⚠️ ${lowStockCount} ${this.t("lowStock")}
                </span>
              ` : ""}
            </div>
            <p style="margin:4px 0 0 0; font-size:13px; color:var(--secondary-text-color, #64748b);">
              ${this.t("partsSubtitle")}
            </p>
          </div>
          <button class="btn btn-primary" id="btn-add-part" style="flex-shrink:0;">+ ${this.t("addPart")}</button>
        </div>

        ${parts.length === 0 ? `
          <div style="text-align: center; padding: 48px 16px; color: var(--secondary-text-color, #64748b);">
            <div style="font-size: 44px; margin-bottom: 12px;">📦</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 14px;">${this.t("noParts")}</div>
            <button class="btn btn-primary" id="btn-empty-add-part">+ ${this.t("addPart")}</button>
          </div>
        ` : `
          <div class="parts-grid">
            ${parts.map(p => this._renderPartCard(p)).join("")}
          </div>
        `}
      `;
    }

    _renderPartCard(part) {
      const stock = parseFloat(part.stock || 0);
      const minStock = parseFloat(part.min_stock !== undefined ? part.min_stock : 1);
      const isLow = stock <= minStock;
      const linkedThing = part.thing_id ? (this._data.things || []).find(th => th.id === part.thing_id) : null;

      return `
        <div class="part-card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
            <div>
              <div style="font-weight:700; font-size:15px; color:var(--primary-text-color, inherit);">${this._escape(part.name)}</div>
              ${part.part_number ? `
                <div style="font-size:11px; color:var(--secondary-text-color, #64748b); font-family:monospace; margin-top:2px;">
                  SKU: ${this._escape(part.part_number)}
                </div>
              ` : ""}
            </div>
            <div style="display:flex; gap:4px;">
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px;" data-edit-part="${part.id}" title="${this.t("edit")}">✏️</button>
              <button class="btn btn-secondary" style="padding:4px 6px; font-size:11px; color:var(--error-color, #ef4444);" data-delete-part="${part.id}" title="${this.t("delete")}">🗑️</button>
            </div>
          </div>

          <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
            <span class="badge-pill" style="background:${isLow ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)"}; color:${isLow ? "#ef4444" : "#10b981"}; font-weight:700; font-size:12px; padding:4px 10px;">
              ${isLow ? "⚠️ " + this.t("lowStock") : "✓ " + this.t("inStock")}: ${stock} ${this._escape(part.unit || "pcs")}
            </span>
            <span style="font-size:11px; color:var(--secondary-text-color, #64748b);">
              (Min: ${minStock} ${this._escape(part.unit || "pcs")})
            </span>
            ${part.unit_price ? `
              <span class="meta-chip" style="background:rgba(59, 130, 246, 0.12); color:#2563eb;">
                💰 ${parseFloat(part.unit_price).toFixed(2)} €
              </span>
            ` : ""}
            ${linkedThing ? `
              <span class="meta-chip" style="background:rgba(2, 132, 199, 0.12); color:#0284c7;">
                ⚙️ ${this._escape(linkedThing.name)}
              </span>
            ` : ""}
            ${part.storage_location ? `
              <span class="meta-chip" style="background:rgba(100, 116, 139, 0.12); color:#64748b;">
                📍 ${this._escape(part.storage_location)}
              </span>
            ` : ""}
          </div>

          ${part.notes ? `
            <div style="font-size:12px; color:var(--secondary-text-color, #64748b); line-height:1.4;">
              ${this._escape(part.notes)}
            </div>
          ` : ""}

          <div style="display:flex; gap:6px; margin-top:4px;">
            <button class="btn btn-secondary" style="flex:1; padding:6px;" data-part-adjust="${part.id}" data-delta="-1">-1</button>
            <button class="btn btn-secondary" style="flex:1; padding:6px;" data-part-adjust="${part.id}" data-delta="1">+1</button>
            ${part.reorder_url ? `
              <a href="${this._escape(part.reorder_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="flex:2; text-decoration:none; display:flex; align-items:center; justify-content:center; gap:4px; padding:6px; font-size:12px;">
                🛒 ${this.t("reorder")}
              </a>
            ` : ""}
          </div>
        </div>
      `;
    }


    // ================= VIEW: LEADERBOARD =================
    _renderLeaderboardView() {
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;
      if (!isGamification) {
        return `
          <div style="max-width: 600px; margin: 40px auto; text-align: center; padding: 40px 20px; background: var(--card-background-color, #ffffff); border-radius: 14px; border: 1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2)));">
            <div style="font-size: 48px; margin-bottom: 12px;">🏆</div>
            <h3 style="margin: 0 0 8px 0; font-size: 18px; color: var(--primary-text-color, inherit);">${this.t("gamificationDisabledTitle")}</h3>
            <p style="color: var(--secondary-text-color, #64748b); font-size: 14px; margin: 0 0 20px 0;">
              ${this.t("gamificationDisabledDesc")}
            </p>
            <button class="btn btn-primary" id="btn-goto-settings-from-leaderboard">${this.t("settings")}</button>
          </div>
        `;
      }

      const sortedUsers = [...this._data.users].sort((a, b) => (b.points || 0) - (a.points || 0));

      return `
        <div style="max-width: 900px; margin: 0 auto;">
          <h2 style="margin: 0 0 18px 0; font-size: 20px;">🏆 ${this.t("leaderboardAndStreaks")}</h2>

          <div class="leaderboard-cards">
            ${sortedUsers.map((u, index) => `
              <div class="leaderboard-card">
                <div class="rank-badge">${index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : "⭐"}</div>
                <div class="user-avatar" style="background:${u.color}; width:48px; height:48px; font-size:20px;">
                  ${u.name.slice(0, 1).toUpperCase()}
                </div>
                <div style="font-weight:700; font-size:16px;">${this._escape(u.name)}</div>
                <div class="points-huge">${u.points || 0} <span style="font-size:14px; font-weight:500;">${this.t("pts")}</span></div>
                <div style="display:flex; gap:12px; font-size:12px; color:var(--secondary-text-color, #64748b);">
                  <span>🔥 ${u.streak || 0} ${this.t("dayStreak")}</span>
                  <span>✓ ${u.completed_count || 0} ${this.t("tasksDone")}</span>
                </div>
              </div>
            `).join("")}
          </div>

          <h3 style="margin: 24px 0 12px 0; font-size: 16px;">📜 ${this.t("recentActivity")}</h3>
          <div class="activity-timeline">
            ${this._data.activity_log && this._data.activity_log.length > 0 ? (
              this._data.activity_log.slice(-15).reverse().map(act => `
                <div class="activity-row">
                  <div style="font-size:16px;">
                    ${act.action === "task_completed" ? "✅" : act.action === "task_created" ? "📝" : "⚙️"}
                  </div>
                  <div style="flex:1;">
                    <strong>${this._escape(act.title || act.name || act.action)}</strong>
                    ${act.user_id ? `<span> ${this.t("by")} ${this._getUserName(act.user_id)}</span>` : ""}
                    ${act.points ? `<span style="color:#d97706; font-weight:600;"> (+${act.points} ${this.t("pts")})</span>` : ""}
                  </div>
                  <div style="font-size:11px; color:var(--secondary-text-color, #64748b);">
                    ${act.timestamp ? act.timestamp.slice(11, 16) : ""}
                  </div>
                </div>
              `).join("")
            ) : `<p style="color:var(--secondary-text-color, #64748b); font-size:13px;">${this.t("noRecentActivity")}</p>`}
          </div>
        </div>
      `;
    }

    _getUserName(userId) {
      const u = this._data.users.find(user => user.id === userId);
      return u ? u.name : userId;
    }

    // ================= VIEW: SETTINGS =================
    _renderSettingsView() {
      const s = this._data.settings || {};
      const isGamification = s.gamification_enabled !== false;

      return `
        <div style="max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px;">
          <!-- Members Management -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
              <h3 style="margin:0; font-size:16px;">👥 ${this.t("householdMembers")}</h3>
              <button class="btn btn-secondary" id="btn-add-user">+ ${this.t("addUser")}</button>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px;">
              ${this._data.users.map(u => `
                <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 12px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); border-radius:8px;">
                  <div style="display:flex; align-items:center; gap:10px;">
                    <div class="user-avatar" style="background:${u.color}; width:28px; height:28px;">
                      ${u.name.slice(0, 1).toUpperCase()}
                    </div>
                    <strong>${this._escape(u.name)}</strong>
                    ${isGamification ? `<span style="font-size:12px; color:var(--secondary-text-color, #64748b);">(${u.points || 0} ${this.t("pts")})</span>` : ""}
                  </div>
                  <div style="display:flex; gap:6px;">
                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:11px;" data-edit-user="${u.id}" title="${this.t("edit")}">✏️</button>
                    <button class="btn btn-secondary" style="padding:4px 8px; font-size:11px; color:var(--error-color, #ef4444);" data-delete-user="${u.id}" title="${this.t("delete")}">🗑️</button>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>

          <!-- Labels Management -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
              <h3 style="margin:0; font-size:16px;">🏷️ ${this.t("labelsAndCategories")}</h3>
              <button class="btn btn-secondary" id="btn-add-label">+ ${this.t("addLabel")}</button>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">
              ${this._data.labels.map(l => `
                <div style="display:flex; align-items:center; gap:6px; padding:4px 10px; border-radius:20px; background:${l.color}18; color:${l.color}; font-size:13px; font-weight:600;">
                  <span>${this._escape(l.name)}</span>
                  <button style="border:none; background:transparent; cursor:pointer; color:inherit; font-size:12px;" data-edit-label="${l.id}" title="${this.t("edit")}">✏️</button>
                  <button style="border:none; background:transparent; cursor:pointer; color:inherit; font-size:12px;" data-delete-label="${l.id}" title="${this.t("delete")}">×</button>
                </div>
              `).join("")}
            </div>
          </div>

          <!-- External Providers Management -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px; flex-wrap:wrap; gap:10px;">
              <div>
                <h3 style="margin:0 0 4px 0; font-size:16px;">🔗 ${this.t("providers")}</h3>
                <p style="margin:0; font-size:12px; color:var(--secondary-text-color, #64748b); max-width:540px;">
                  ${this.t("providersSubtitle")}
                </p>
                <div style="margin-top:6px; font-size:11px; color:var(--primary-color, #2563eb);">
                  📅 ${this.t("calendarSyncHint")}
                </div>
              </div>
              <div style="display:flex; gap:8px;">
                <button class="btn btn-secondary" id="btn-sync-providers" title="${this.t("syncProviders")}">🔄 ${this.t("syncProviders")}</button>
                <button class="btn btn-primary" id="btn-link-provider">+ ${this.t("linkProvider")}</button>
              </div>
            </div>

            <div style="display:flex; flex-direction:column; gap:8px;">
              ${(!this._data.providers || this._data.providers.length === 0) ? `
                <div style="text-align:center; padding:24px; color:var(--secondary-text-color, #64748b); font-size:13px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); border-radius:8px;">
                  <div style="font-size:24px; margin-bottom:6px;">📋</div>
                  <div>${this.t("noProvidersLinked")}</div>
                </div>
              ` : `
                ${this._data.providers.map(p => `
                  <div class="provider-row" style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); border-radius:8px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.12)));">
                    <div style="display:flex; align-items:center; gap:12px;">
                      <div style="width:36px; height:36px; border-radius:8px; background:var(--card-background-color, rgba(127,127,127,0.15)); display:flex; align-items:center; justify-content:center; font-size:18px;">
                        ${p.provider_type === "google_tasks" ? "🌐" : p.provider_type === "todoist" ? "☑️" : p.provider_type === "caldav" ? "📅" : p.provider_type === "bring" ? "🛒" : p.provider_type === "shopping_list" ? "🛍️" : "📝"}
                      </div>
                      <div>
                        <div style="font-weight:700; font-size:14px;">${this._escape(p.name || p.entity_id)}</div>
                        <div style="font-size:12px; color:var(--secondary-text-color, #64748b);">${this._escape(p.entity_id)} <span style="display:inline-block; margin-left:6px; padding:1px 6px; border-radius:10px; background:var(--divider-color, rgba(127,127,127,0.2)); font-size:10px; text-transform:uppercase;">${this._escape(p.provider_type || "generic")}</span></div>
                      </div>
                    </div>
                    <button class="btn btn-secondary" style="padding:4px 10px; font-size:12px; color:var(--error-color, #ef4444);" data-unlink-provider="${p.entity_id}">
                      🗑️ ${this.t("unlinkProvider")}
                    </button>
                  </div>
                `).join("")}
              `}
            </div>
          </div>

          <!-- System Preferences -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding:20px;">
            <h3 style="margin:0 0 16px 0; font-size:16px;">⚙️ ${this.t("preferences")}</h3>
            <div style="display:flex; flex-direction:column; gap:12px;">
              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-gamification" ${s.gamification_enabled !== false ? "checked" : ""}>
                <span>${this.t("gamificationEnabled")}</span>
              </label>

              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-sounds" ${s.sound_enabled ? "checked" : ""}>
                <span>${this.t("soundEnabled")}</span>
              </label>

              <label style="display:flex; align-items:center; gap:10px; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="pref-confetti" ${s.confetti_enabled ? "checked" : ""}>
                <span>${this.t("confettiEnabled")}</span>
              </label>

              <div class="form-group" id="pref-default-points-group" style="max-width:240px; margin-top:8px; display:${isGamification ? "flex" : "none"}; flex-direction:column;">
                <label class="form-label">${this.t("defaultPoints")}</label>
                <input type="number" class="text-input" id="pref-default-points" value="${s.default_points || 10}">
              </div>

              <div class="form-group" style="max-width:240px; margin-top:8px;">
                <label class="form-label">${this.t("language")}</label>
                <select class="select-input" id="pref-language">
                  <option value="auto" ${(!s.language || s.language === "auto") ? "selected" : ""}>${this.t("langAuto")}</option>
                  <option value="en" ${s.language === "en" ? "selected" : ""}>${this.t("langEn")}</option>
                  <option value="de" ${s.language === "de" ? "selected" : ""}>${this.t("langDe")}</option>
                </select>
              </div>

              <button class="btn btn-primary" style="align-self:flex-start; margin-top:10px;" id="btn-save-prefs">
                ${this.t("save")}
              </button>
            </div>
          </div>

          <!-- Backup & Restore -->
          <div style="background:var(--card-background-color, #ffffff); border-radius:14px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); padding:20px;">
            <h3 style="margin:0 0 12px 0; font-size:16px;">💾 ${this.t("backupAndRestore")}</h3>
            <p style="font-size:13px; color:var(--secondary-text-color, #64748b); margin-top:0;">${this.t("backupDescription")}</p>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <button class="btn btn-secondary" id="btn-export-backup">📥 ${this.t("exportBackup")}</button>
              <label class="btn btn-secondary" style="cursor:pointer;">
                📤 ${this.t("importBackup")}
                <input type="file" id="input-import-backup" accept=".json" style="display:none;">
              </label>
            </div>
          </div>
        </div>
      `;
    }

    // ================= MODALS =================
    _renderModal() {
      if (!this._modalState) return "";
      const { type } = this._modalState;

      if (type === "task") return this._renderTaskModal();
      if (type === "thing") return this._renderThingModal();
      if (type === "part") return this._renderPartModal();
      if (type === "complete_details") return this._renderCompleteDetailsModal();
      if (type === "qr_code") return this._renderQrCodeModal();
      if (type === "user") return this._renderUserModal();
      if (type === "label") return this._renderLabelModal();
      if (type === "link_provider") return this._renderLinkProviderModal();
      return "";
    }

    _renderLinkProviderModal() {
      const entities = this._availableTodoEntities || [];
      const linkedIds = new Set((this._data.providers || []).map(p => p.entity_id));
      const unlinked = entities.filter(e => !linkedIds.has(e.entity_id));
      const isLoading = Boolean(this._loadingTodoEntities && entities.length === 0);
      const isManual = Boolean(this._modalState && this._modalState.manualMode);

      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              🔗 ${this.t("linkProvider")}
            </h2>

            <p style="font-size:13px; color:var(--secondary-text-color, #64748b); margin-top:0;">
              ${this.t("providersSubtitle")}
            </p>

            ${isLoading ? `
              <div class="form-group">
                <label class="form-label">${this.t("selectTodoEntity")}</label>
                <div style="font-size:13px; color:var(--secondary-text-color, #64748b); padding:8px 0;">
                  ⌛ ${this.t("loadingEntities")}
                </div>
              </div>
            ` : (unlinked.length > 0 && !isManual) ? `
              <div class="form-group">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                  <label class="form-label" style="margin:0;">${this.t("selectTodoEntity")}</label>
                  <a href="#" id="btn-toggle-manual-provider" style="font-size:12px; color:var(--primary-color, #2563eb); text-decoration:none; cursor:pointer;">
                    ✏️ ${this.t("enterManually")}
                  </a>
                </div>
                <select class="select-input" id="m-provider-entity">
                  ${unlinked.map(e => `
                    <option value="${e.entity_id}">
                      ${this._escape(e.name)} (${this._escape(e.provider_name || e.provider_type)}) - ${e.entity_id}
                    </option>
                  `).join("")}
                </select>
              </div>
            ` : `
              <div class="form-group">
                ${unlinked.length > 0 ? `
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <label class="form-label" style="margin:0;">${this.t("manualEntityId")}</label>
                    <a href="#" id="btn-toggle-manual-provider" style="font-size:12px; color:var(--primary-color, #2563eb); text-decoration:none; cursor:pointer;">
                      📋 ${this.t("chooseFromList")}
                    </a>
                  </div>
                ` : `
                  <div style="font-size:13px; color:var(--secondary-text-color, #64748b); padding:8px 12px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); border-radius:8px; margin-bottom:12px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2)));">
                    ℹ️ ${this.t("noEntitiesFound")} ${this.t("enterManuallyHint")}
                  </div>
                  <label class="form-label">${this.t("manualEntityId")}</label>
                `}
                <input type="text" class="text-input" id="m-provider-entity-manual" placeholder="todo.shopping_list" value="">
              </div>
            `}

            <div class="form-group">
              <label class="form-label">${this.t("providerName")} (${this.t("optional")})</label>
              <input type="text" class="text-input" id="m-provider-name" placeholder="e.g. Shopping List, Work Tasks">
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-provider">
                ${this.t("save")}
              </button>
            </div>
          </div>
        </div>
      `;
    }

    _renderTaskModal() {
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;
      const task = this._modalState.task;
      const rec = task.recurrence || {};
      const subtasks = task.subtasks || [];

      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${task.id ? this.t("editTask") : this.t("addTask")}
            </h2>

            ${task.is_external ? `
              <div style="font-size:13px; padding:8px 12px; background:rgba(2, 132, 199, 0.12); border-radius:8px; color:var(--primary-color, #0284c7); border:1px solid rgba(2, 132, 199, 0.25); margin-bottom:8px;">
                🔗 <strong>${this.t("externalTask")}:</strong> ${this._escape(task.provider_name || task.provider_entity_id)}
              </div>
            ` : ""}

            ${!task.id && this._data.providers && this._data.providers.length > 0 ? `
              <div class="form-group">
                <label class="form-label">${this.t("destinationList")}</label>
                <select class="select-input" id="m-task-dest">
                  <option value="task_manager">🏠 ${this.t("taskManagerList")}</option>
                  ${this._data.providers.map(p => `
                    <option value="${p.entity_id}">🔗 ${this._escape(p.name || p.entity_id)}</option>
                  `).join("")}
                </select>
              </div>
            ` : ""}

            <!-- Active / Paused Toggle -->
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; background:var(--secondary-background-color, rgba(127,127,127,0.06)); padding:10px 14px; border-radius:8px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.15)));">
              <div>
                <div style="font-weight:600; font-size:13px; display:flex; align-items:center; gap:6px;">
                  <span id="m-task-status-text">${task.is_active === false ? "⏸️ " + this.t("isPaused") : "✅ " + this.t("isActive")}</span>
                </div>
                <div style="font-size:11px; color:var(--secondary-text-color, #64748b); margin-top:2px;">${this.t("isActiveHint")}</div>
              </div>
              <div style="display:flex; align-items:center; gap:10px;">
                ${task.id ? `
                  <button type="button" class="btn btn-secondary" id="m-task-btn-pause-toggle" style="padding:6px 12px; font-size:12px; display:inline-flex; align-items:center; gap:5px;">
                    ${task.is_active === false ? "▶️ " + this.t("resumeTask") : "⏸️ " + this.t("pauseTask")}
                  </button>
                ` : ""}
                <input type="checkbox" id="m-task-is-active" ${task.is_active !== false ? "checked" : ""} style="width:18px; height:18px; cursor:pointer;" title="${this.t("isActive")}">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("titleLabel")}</label>
              <input type="text" class="text-input" id="m-task-title" value="${this._escape(task.title)}" placeholder="${this.t("titlePlaceholder")}">
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("descriptionLabel")}</label>
              <textarea class="text-input" id="m-task-desc" rows="2" placeholder="${this.t("descriptionPlaceholder")}">${this._escape(task.description)}</textarea>
            </div>

            <!-- Task Type (Chore vs Reading) -->
            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("taskTypeLabel")}</label>
                <select class="select-input" id="m-task-type">
                  <option value="chore" ${task.task_type !== "reading" ? "selected" : ""}>🧹 ${this.t("taskTypeChore")}</option>
                  <option value="reading" ${task.task_type === "reading" ? "selected" : ""}>📟 ${this.t("taskTypeReading")}</option>
                </select>
              </div>
              <div class="form-group" id="m-task-reading-unit-group" style="display:${task.task_type === "reading" ? "block" : "none"};">
                <label class="form-label">${this.t("readingUnitLabel")}</label>
                <input type="text" class="text-input" id="m-task-reading-unit" value="${this._escape(task.reading_unit || "")}" placeholder="m³, kWh, L, bar">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">⏱️ ${this.t("durationMinutesLabel")}</label>
                <input type="number" class="text-input" id="m-task-duration" value="${task.default_duration_minutes || ""}" placeholder="30">
              </div>
              <div class="form-group">
                <label class="form-label">💰 ${this.t("costLabel")}</label>
                <input type="number" step="0.01" class="text-input" id="m-task-cost" value="${task.default_cost || ""}" placeholder="0.00">
              </div>
            </div>

            <!-- Action on Completion -->
            <div class="form-group">
              <label class="form-label">⚡ ${this.t("onCompleteEntityLabel")}</label>
              <input type="text" class="text-input" id="m-task-on-complete-entity" value="${this._escape(task.on_complete_entity_id || "")}" placeholder="${this.t("onCompleteEntityPlaceholder")}">
            </div>

            <!-- Tags -->
            <div class="form-group">
              <label class="form-label">🏷️ ${this.t("tags")}</label>
              <input type="text" class="text-input" id="m-task-tags" value="${this._escape((task.tags || []).join(", "))}" placeholder="${this.t("tagsPlaceholder")}">
            </div>

            <!-- Dependencies -->
            <div class="form-group">
              <label class="form-label">🔗 ${this.t("dependencies")}</label>
              <div style="font-size:11px; color:var(--secondary-text-color, #64748b); margin-bottom:4px;">${this.t("dependenciesHint")}</div>
              <select class="select-input" id="m-task-dependencies" multiple size="3" style="height:auto; min-height:64px;">
                ${this._data.tasks.filter(t => t.id !== task.id).map(t => `
                  <option value="${t.id}" ${(task.dependencies || []).includes(t.id) ? "selected" : ""}>
                    ${this._escape(t.title)} (${t.status === "completed" ? "✓" : "⏳"})
                  </option>
                `).join("")}
              </select>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("dueDate")}</label>
                <input type="date" class="text-input" id="m-task-date" value="${task.due_date || ""}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("dueTime")}</label>
                <input type="time" class="text-input" id="m-task-time" value="${task.due_time || ""}">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">⏳ ${this.t("dueSoonDays")}</label>
                <input type="number" class="text-input" id="m-task-due-soon-days" value="${task.due_soon_days !== undefined ? task.due_soon_days : 0}" min="0">
              </div>
              <div class="form-group">
                <label class="form-label">🔔 ${this.t("notificationInterval")}</label>
                <input type="number" class="text-input" id="m-task-notification-interval" value="${task.notification_interval !== undefined ? task.notification_interval : 1}" min="1">
              </div>
            </div>

            <!-- Reminders -->
            <div class="form-group">
              <label class="form-label">🔔 ${this.t("reminders")}</label>
              <div style="display:flex; flex-wrap:wrap; gap:8px;">
                ${[
                  { val: 0, label: this.t("atDueTime") },
                  { val: 15, label: this.t("minBefore", { min: "15" }) },
                  { val: 60, label: this.t("hoursBefore", { hours: "1" }) },
                  { val: 1440, label: this.t("daysBefore", { days: "1" }) }
                ].map(r => {
                  const checked = (task.reminders || []).includes(r.val);
                  return `
                    <label style="display:flex; align-items:center; gap:4px; font-size:12px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); padding:4px 8px; border-radius:6px; cursor:pointer;">
                      <input type="checkbox" class="m-reminder-checkbox" value="${r.val}" ${checked ? "checked" : ""}>
                      <span>${r.label}</span>
                    </label>
                  `;
                }).join("")}
              </div>
            </div>

            ${isGamification ? `
              <div class="form-grid-2">
                <div class="form-group">
                  <label class="form-label">${this.t("priority")}</label>
                  <select class="select-input" id="m-task-priority">
                    <option value="none" ${task.priority === "none" ? "selected" : ""}>${this.t("priorityNone")}</option>
                    <option value="p1" ${task.priority === "p1" ? "selected" : ""}>${this.t("priorityP1")}</option>
                    <option value="p2" ${task.priority === "p2" ? "selected" : ""}>${this.t("priorityP2")}</option>
                    <option value="p3" ${task.priority === "p3" ? "selected" : ""}>${this.t("priorityP3")}</option>
                    <option value="p4" ${task.priority === "p4" ? "selected" : ""}>${this.t("priorityP4")}</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">${this.t("pointsReward")}</label>
                  <input type="number" class="text-input" id="m-task-points" value="${task.points !== undefined ? task.points : 10}">
                </div>
              </div>
            ` : `
              <div class="form-group">
                <label class="form-label">${this.t("priority")}</label>
                <select class="select-input" id="m-task-priority">
                  <option value="none" ${task.priority === "none" ? "selected" : ""}>${this.t("priorityNone")}</option>
                  <option value="p1" ${task.priority === "p1" ? "selected" : ""}>${this.t("priorityP1")}</option>
                  <option value="p2" ${task.priority === "p2" ? "selected" : ""}>${this.t("priorityP2")}</option>
                  <option value="p3" ${task.priority === "p3" ? "selected" : ""}>${this.t("priorityP3")}</option>
                  <option value="p4" ${task.priority === "p4" ? "selected" : ""}>${this.t("priorityP4")}</option>
                </select>
                <input type="hidden" id="m-task-points" value="${task.points !== undefined ? task.points : 10}">
              </div>
            `}

            <!-- Assignee & Rotation -->
            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("assignee")}</label>
                <select class="select-input" id="m-task-assignee">
                  <option value="">${this.t("none")}</option>
                  ${this._data.users.map(u => `
                    <option value="${u.id}" ${u.id === task.current_assignee ? "selected" : ""}>${u.name}</option>
                  `).join("")}
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">${this.t("rotation")}</label>
                <select class="select-input" id="m-task-rotation">
                  <option value="none" ${task.rotation_mode === "none" ? "selected" : ""}>${this.t("noneFixed")}</option>
                  <option value="round_robin" ${task.rotation_mode === "round_robin" ? "selected" : ""}>${this.t("roundRobin")}</option>
                  <option value="least_completed" ${task.rotation_mode === "least_completed" ? "selected" : ""}>${this.t("leastCompleted")}</option>
                  <option value="random" ${task.rotation_mode === "random" ? "selected" : ""}>${this.t("random")}</option>
                </select>
              </div>
            </div>

            <!-- Recurrence -->
            <div style="border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); border-radius:10px; padding:12px; background:var(--secondary-background-color, rgba(127,127,127,0.04));">
              <label style="display:flex; align-items:center; gap:8px; font-weight:600; font-size:14px; cursor:pointer;">
                <input type="checkbox" id="m-task-rec-enable" ${rec.enabled ? "checked" : ""}>
                <span>${this.t("recurrenceSchedule")}</span>
              </label>

              <div id="m-rec-fields" style="display:${rec.enabled ? "flex" : "none"}; flex-direction:column; gap:10px; margin-top:10px;">
                <div class="form-group">
                  <label class="form-label">${this.t("repeatMode")}</label>
                  <select class="select-input" id="m-task-rec-mode">
                    <option value="after" ${(rec.repeat_mode || "after") === "after" ? "selected" : ""}>🔄 ${this.t("repeatModeAfter")}</option>
                    <option value="every" ${(rec.repeat_mode || "") === "every" ? "selected" : ""}>📅 ${this.t("repeatModeEvery")}</option>
                  </select>
                </div>

                <!-- Mode 'after' fields -->
                <div id="m-rec-mode-after" class="form-grid-2" style="display:${(rec.repeat_mode || "after") === "after" ? "grid" : "none"};">
                  <div class="form-group">
                    <label class="form-label">${this.t("type")}</label>
                    <select class="select-input" id="m-task-rec-type">
                      <option value="daily" ${rec.type === "daily" ? "selected" : ""}>${this.t("daily")}</option>
                      <option value="weekly" ${rec.type === "weekly" ? "selected" : ""}>${this.t("weekly")}</option>
                      <option value="monthly" ${rec.type === "monthly" ? "selected" : ""}>${this.t("monthly")}</option>
                      <option value="yearly" ${rec.type === "yearly" ? "selected" : ""}>${this.t("yearly")}</option>
                      <option value="custom_days" ${rec.type === "custom_days" ? "selected" : ""}>${this.t("customDays")}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label class="form-label">${this.t("interval")}</label>
                    <input type="number" class="text-input" id="m-task-rec-interval" value="${rec.interval || 1}" min="1">
                  </div>
                  <div id="m-rec-weekdays" class="form-group" style="grid-column: span 2; display:${rec.type === "weekly" ? "block" : "none"};">
                    <label class="form-label">${this.t("weekdaysLabel")}</label>
                    <div style="display:flex; gap:6px; flex-wrap:wrap;">
                      ${[
                        { id: 0, label: "Mo" },
                        { id: 1, label: "Di" },
                        { id: 2, label: "Mi" },
                        { id: 3, label: "Do" },
                        { id: 4, label: "Fr" },
                        { id: 5, label: "Sa" },
                        { id: 6, label: "So" }
                      ].map(w => {
                        const isSel = (rec.weekdays || rec.days_of_week || []).includes(w.id);
                        return `
                          <label style="display:flex; align-items:center; gap:4px; font-size:12px; background:var(--secondary-background-color, rgba(127,127,127,0.08)); padding:4px 8px; border-radius:6px; cursor:pointer;">
                            <input type="checkbox" class="m-weekday-checkbox" value="${w.id}" ${isSel ? "checked" : ""}>
                            <span>${w.label}</span>
                          </label>
                        `;
                      }).join("")}
                    </div>
                  </div>
                  <div class="form-group" style="grid-column: span 2;">
                    <label class="form-label">${this.t("recurrenceCadence")}</label>
                    <select class="select-input" id="m-task-rec-based">
                      <option value="due_date" ${rec.based_on === "due_date" ? "selected" : ""}>${this.t("cadenceDueDate")}</option>
                      <option value="completion_date" ${rec.based_on === "completion_date" ? "selected" : ""}>${this.t("cadenceCompletionDate")}</option>
                    </select>
                  </div>
                </div>

                <!-- Mode 'every' calendar schedule fields -->
                <div id="m-rec-mode-every" style="display:${(rec.repeat_mode || "") === "every" ? "flex" : "none"}; flex-direction:column; gap:10px;">
                  <div class="form-group">
                    <label class="form-label">${this.t("repeatMode")}</label>
                    <select class="select-input" id="m-task-rec-every-type">
                      <option value="repeat_every_weekday" ${rec.repeat_every_type === "repeat_every_weekday" ? "selected" : ""}>${this.t("repeatEveryWeekday")}</option>
                      <option value="repeat_every_day_of_month" ${rec.repeat_every_type === "repeat_every_day_of_month" ? "selected" : ""}>${this.t("repeatEveryDayOfMonth")}</option>
                      <option value="repeat_every_weekday_of_month" ${rec.repeat_every_type === "repeat_every_weekday_of_month" ? "selected" : ""}>${this.t("repeatEveryWeekdayOfMonth")}</option>
                      <option value="repeat_every_days_before_end_of_month" ${rec.repeat_every_type === "repeat_every_days_before_end_of_month" ? "selected" : ""}>${this.t("repeatEveryDaysBeforeEndOfMonth")}</option>
                    </select>
                  </div>
                  <div id="m-every-weekday-group" class="form-group" style="display:${(!rec.repeat_every_type || rec.repeat_every_type === "repeat_every_weekday") ? "block" : "none"};">
                    <label class="form-label">${this.t("weekdaysLabel")}</label>
                    <select class="select-input" id="m-task-every-weekday">
                      <option value="0" ${rec.repeat_every_weekday === 0 ? "selected" : ""}>Mo (Montag / Monday)</option>
                      <option value="1" ${rec.repeat_every_weekday === 1 ? "selected" : ""}>Di (Dienstag / Tuesday)</option>
                      <option value="2" ${rec.repeat_every_weekday === 2 ? "selected" : ""}>Mi (Mittwoch / Wednesday)</option>
                      <option value="3" ${rec.repeat_every_weekday === 3 ? "selected" : ""}>Do (Donnerstag / Thursday)</option>
                      <option value="4" ${rec.repeat_every_weekday === 4 ? "selected" : ""}>Fr (Freitag / Friday)</option>
                      <option value="5" ${rec.repeat_every_weekday === 5 ? "selected" : ""}>Sa (Samstag / Saturday)</option>
                      <option value="6" ${rec.repeat_every_weekday === 6 ? "selected" : ""}>So (Sonntag / Sunday)</option>
                    </select>
                  </div>
                  <div id="m-every-day-group" class="form-group" style="display:${rec.repeat_every_type === "repeat_every_day_of_month" ? "block" : "none"};">
                    <label class="form-label">${this.t("repeatEveryDayOfMonth")}</label>
                    <input type="number" class="text-input" id="m-task-every-day" value="${rec.repeat_every_day_of_month || 1}" min="1" max="31">
                  </div>
                  <div id="m-every-weekday-month-group" class="form-grid-2" style="display:${rec.repeat_every_type === "repeat_every_weekday_of_month" ? "grid" : "none"};">
                    <div class="form-group">
                      <label class="form-label">N-ter (1-5)</label>
                      <select class="select-input" id="m-task-every-nth">
                        <option value="1" ${rec.repeat_every_nth === 1 ? "selected" : ""}>1.</option>
                        <option value="2" ${rec.repeat_every_nth === 2 ? "selected" : ""}>2.</option>
                        <option value="3" ${rec.repeat_every_nth === 3 ? "selected" : ""}>3.</option>
                        <option value="4" ${rec.repeat_every_nth === 4 ? "selected" : ""}>4.</option>
                        <option value="5" ${rec.repeat_every_nth === 5 ? "selected" : ""}>5.</option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label class="form-label">${this.t("weekdaysLabel")}</label>
                      <select class="select-input" id="m-task-every-nth-weekday">
                        <option value="0" ${rec.repeat_every_weekday === 0 ? "selected" : ""}>Mo</option>
                        <option value="1" ${rec.repeat_every_weekday === 1 ? "selected" : ""}>Di</option>
                        <option value="2" ${rec.repeat_every_weekday === 2 ? "selected" : ""}>Mi</option>
                        <option value="3" ${rec.repeat_every_weekday === 3 ? "selected" : ""}>Do</option>
                        <option value="4" ${rec.repeat_every_weekday === 4 ? "selected" : ""}>Fr</option>
                        <option value="5" ${rec.repeat_every_weekday === 5 ? "selected" : ""}>Sa</option>
                        <option value="6" ${rec.repeat_every_weekday === 6 ? "selected" : ""}>So</option>
                      </select>
                    </div>
                  </div>
                  <div id="m-every-days-before-group" class="form-group" style="display:${rec.repeat_every_type === "repeat_every_days_before_end_of_month" ? "block" : "none"};">
                    <label class="form-label">${this.t("repeatEveryDaysBeforeEndOfMonth")}</label>
                    <input type="number" class="text-input" id="m-task-every-days-before" value="${rec.repeat_every_days_before_end_of_month || 1}" min="1" max="30">
                  </div>
                </div>
              </div>
            </div>

            <!-- Subtasks Checklist -->
            <div class="form-group">
              <label class="form-label">${this.t("subtasksHint")}</label>
              <div id="subtasks-container" style="display:flex; flex-direction:column; gap:6px;">
                ${subtasks.map((st, i) => `
                  <div style="display:flex; gap:6px;">
                    <input type="text" class="text-input m-subtask-input" value="${this._escape(st.title)}" placeholder="${this.t("newSubtaskPlaceholder")}" style="flex:1;">
                    <button class="btn btn-secondary btn-del-subtask" data-index="${i}">×</button>
                  </div>
                `).join("")}
              </div>
              <button class="btn btn-secondary" style="align-self:flex-start; margin-top:6px; font-size:12px;" id="btn-add-subtask-row">
                ${this.t("addSubtaskStep")}
              </button>
            </div>

            <!-- Linked Thing -->
            <div class="form-group">
              <label class="form-label">${this.t("linkedThing")}</label>
              <select class="select-input" id="m-task-linked-thing">
                <option value="">${this.t("none")}</option>
                ${this._data.things.map(th => `
                  <option value="${th.id}" ${th.id === task.linked_thing_id ? "selected" : ""}>
                    ${th.name} (${th.current_value} / ${th.threshold_operator || ">="} ${th.target_value} ${th.unit || ""})
                  </option>
                `).join("")}
              </select>
              <div id="m-task-thing-hint" style="background:rgba(2, 132, 199, 0.12); border:1px solid rgba(2, 132, 199, 0.25); border-radius:6px; padding:8px 12px; font-size:12px; color:var(--primary-color, #0284c7); margin-top:6px; display:${task.linked_thing_id ? "block" : "none"};">
                ${this.t("taskLinkedThingHint")}
              </div>
            </div>

            <!-- Advanced Options & HA Overrides -->
            <details style="margin-top:10px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.15))); border-radius:8px; padding:8px 12px; background:var(--secondary-background-color, rgba(127,127,127,0.03));">
              <summary style="font-weight:600; font-size:13px; cursor:pointer; color:var(--primary-text-color, inherit);">⚙️ ${this.t("advancedOptions")}</summary>
              <div style="margin-top:10px; display:flex; flex-direction:column; gap:10px;">
                <div class="form-group">
                  <label class="form-label">${this.t("activeOverride")}</label>
                  <input type="text" class="text-input" id="m-task-active-override" value="${this._escape(task.active_override || "")}" placeholder="input_boolean.vacation_mode">
                </div>
                <div class="form-group">
                  <label class="form-label">${this.t("intervalOverride")}</label>
                  <input type="text" class="text-input" id="m-task-interval-override" value="${this._escape(task.task_interval_override || "")}" placeholder="input_number.task_interval">
                </div>
                <div class="form-group">
                  <label class="form-label">${this.t("dueSoonOverride")}</label>
                  <input type="text" class="text-input" id="m-task-due-soon-override" value="${this._escape(task.due_soon_override || "")}" placeholder="input_number.due_soon_days">
                </div>
              </div>
            </details>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-task">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderThingModal() {
      const thing = this._modalState.thing;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${thing.id ? this.t("editThing") : this.t("addThing")}
            </h2>

            <div class="form-group">
              <label class="form-label">${this.t("thingNameLabel")}</label>
              <input type="text" class="text-input" id="m-thing-name" value="${this._escape(thing.name)}" placeholder="${this.t("thingNamePlaceholder")}">
            </div>

            <!-- Optional Linked External Numeric Entity -->
            <div class="form-group" style="position:relative;">
              <label class="form-label">${this.t("linkedEntity")}</label>
              <div class="entity-picker-wrapper">
                <input
                  type="text"
                  class="text-input entity-picker-input"
                  id="m-thing-external-entity"
                  value="${this._escape(thing.external_entity_id || "")}"
                  placeholder="${this.t("linkedEntityPlaceholder")}"
                  autocomplete="off"
                >
                <button type="button" class="entity-picker-clear-btn" id="m-thing-external-entity-clear" title="${this.t("clearSelection")}" style="${thing.external_entity_id ? "display:flex;" : "display:none;"}">✕</button>
              </div>
              <div class="entity-dropdown-list" id="m-thing-external-entity-dropdown" style="display:none;"></div>
              <div style="font-size:11px; color:var(--secondary-text-color, #64748b); margin-top:3px;">${this.t("linkedEntityHint")}</div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("categoryLabel")}</label>
                <input type="text" class="text-input" id="m-thing-category" value="${this._escape(thing.category)}" placeholder="${this.t("categoryPlaceholder")}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("unitLabel")}</label>
                <input type="text" class="text-input" id="m-thing-unit" value="${this._escape(thing.unit)}" placeholder="${this.t("unitPlaceholder")}">
              </div>
            </div>

            <!-- Hardware Specs & Warranty -->
            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("manufacturerLabel")}</label>
                <input type="text" class="text-input" id="m-thing-manufacturer" value="${this._escape(thing.manufacturer || "")}" placeholder="${this.t("manufacturerPlaceholder")}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("modelLabel")}</label>
                <input type="text" class="text-input" id="m-thing-model" value="${this._escape(thing.model || "")}" placeholder="${this.t("modelPlaceholder")}">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("serialNumberLabel")}</label>
                <input type="text" class="text-input" id="m-thing-serial" value="${this._escape(thing.serial_number || "")}" placeholder="${this.t("serialNumberPlaceholder")}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("installationDateLabel")}</label>
                <input type="date" class="text-input" id="m-thing-install-date" value="${thing.installation_date || ""}">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("warrantyExpiryLabel")}</label>
                <input type="date" class="text-input" id="m-thing-warranty-expiry" value="${thing.warranty_expiry || ""}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("documentationUrlLabel")}</label>
                <input type="url" class="text-input" id="m-thing-doc-url" value="${this._escape(thing.documentation_url || "")}" placeholder="${this.t("documentationUrlPlaceholder")}">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("thresholdCondition")}</label>
                <select class="select-input" id="m-thing-operator">
                  <option value=">=" ${thing.threshold_operator !== "<=" ? "selected" : ""}>${this.t("thresholdOperatorGte")}</option>
                  <option value="<=" ${thing.threshold_operator === "<=" ? "selected" : ""}>${this.t("thresholdOperatorLte")}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("thresholdValue")}</label>
                <input type="number" step="any" class="text-input" id="m-thing-target" value="${thing.target_value !== undefined ? thing.target_value : 0}">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("currentValue")}</label>
              <input type="number" step="any" class="text-input" id="m-thing-current" value="${thing.current_value !== undefined ? thing.current_value : 0}">
            </div>

            <!-- Optional Completion Script -->
            <div class="form-group" style="position:relative;">
              <label class="form-label">${this.t("completionScript")}</label>
              <div class="entity-picker-wrapper">
                <input
                  type="text"
                  class="text-input entity-picker-input"
                  id="m-thing-script"
                  value="${this._escape(thing.script_entity_id || "")}"
                  placeholder="${this.t("completionScriptPlaceholder")}"
                  autocomplete="off"
                >
                <button type="button" class="entity-picker-clear-btn" id="m-thing-script-clear" title="${this.t("clearSelection")}" style="${thing.script_entity_id ? "display:flex;" : "display:none;"}">✕</button>
              </div>
              <div class="entity-dropdown-list" id="m-thing-script-dropdown" style="display:none;"></div>
              <div style="font-size:11px; color:var(--secondary-text-color, #64748b); margin-top:3px;">${this.t("completionScriptHint")}</div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-thing">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderPartModal() {
      const part = (this._modalState && this._modalState.part) || {};
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${part.id ? this.t("editPart") : this.t("addPart")}
            </h2>

            <div class="form-group">
              <label class="form-label">${this.t("partNameLabel")}</label>
              <input type="text" class="text-input" id="m-part-name" value="${this._escape(part.name || "")}" placeholder="${this.t("partNamePlaceholder")}">
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("partNumberLabel")}</label>
                <input type="text" class="text-input" id="m-part-number" value="${this._escape(part.part_number || "")}" placeholder="${this.t("partNumberPlaceholder")}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("linkedThing")}</label>
                <select class="select-input" id="m-part-thing-id">
                  <option value="">${this.t("none")}</option>
                  ${(this._data.things || []).map(th => `
                    <option value="${th.id}" ${th.id === part.thing_id ? "selected" : ""}>${this._escape(th.name)}</option>
                  `).join("")}
                </select>
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("stockLabel")}</label>
                <input type="number" step="any" class="text-input" id="m-part-stock" value="${part.stock !== undefined ? part.stock : 1}">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("minStockLabel")}</label>
                <input type="number" step="any" class="text-input" id="m-part-min-stock" value="${part.min_stock !== undefined ? part.min_stock : 1}">
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">${this.t("unitLabel")}</label>
                <input type="text" class="text-input" id="m-part-unit" value="${this._escape(part.unit || "pcs")}" placeholder="pcs, L, kg">
              </div>
              <div class="form-group">
                <label class="form-label">${this.t("unitPriceLabel")}</label>
                <input type="number" step="0.01" class="text-input" id="m-part-unit-price" value="${part.unit_price !== undefined ? part.unit_price : 0.0}">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("storageLocationLabel")}</label>
              <input type="text" class="text-input" id="m-part-location" value="${this._escape(part.storage_location || "")}" placeholder="${this.t("storageLocationPlaceholder")}">
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("reorderUrlLabel")}</label>
              <input type="url" class="text-input" id="m-part-reorder-url" value="${this._escape(part.reorder_url || "")}" placeholder="${this.t("reorderUrlPlaceholder")}">
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("descriptionLabel")}</label>
              <textarea class="text-input" id="m-part-notes" rows="2" placeholder="${this.t("descriptionPlaceholder")}">${this._escape(part.notes || "")}</textarea>
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-part">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderCompleteDetailsModal() {
      const task = (this._modalState && this._modalState.task) || {};
      const parts = this._data.parts || [];
      const isReading = task.task_type === "reading";
      const nowIso = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16);
      const preselectedPartIds = new Set((task.consumed_parts || []).map(p => typeof p === "object" ? p.part_id : p));

      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ✓ ${this.t("completeWithDetails")}: ${this._escape(task.title || "")}
            </h2>

            ${isReading ? `
              <div style="background:rgba(6, 182, 212, 0.12); border:1px solid rgba(6, 182, 212, 0.25); border-radius:8px; padding:12px; margin-bottom:14px;">
                <div style="font-weight:600; font-size:13px; color:#0891b2; margin-bottom:6px;">
                  📟 ${this.t("taskTypeReading")}
                </div>
                <div style="font-size:12px; color:var(--secondary-text-color, #64748b); margin-bottom:8px;">
                  ${this.t("lastReadingLabel")}: <strong>${task.last_reading_value !== undefined && task.last_reading_value !== null ? task.last_reading_value : "—"} ${this._escape(task.reading_unit || "")}</strong>
                </div>
                <div class="form-group" style="margin-bottom:0;">
                  <label class="form-label">${this.t("readingValueLabel")} (${this._escape(task.reading_unit || "")})</label>
                  <input type="number" step="any" class="text-input" id="m-comp-reading" placeholder="z. B. ${task.last_reading_value ? (parseFloat(task.last_reading_value) + 5) : 100}">
                  <div id="m-comp-reading-delta" style="font-size:12px; font-weight:600; color:#0891b2; margin-top:4px;"></div>
                </div>
              </div>
            ` : ""}

            ${parts.length > 0 ? `
              <div class="form-group">
                <label class="form-label">📦 ${this.t("consumedPartsLabel")}</label>
                <div style="display:flex; flex-direction:column; gap:6px; max-height:160px; overflow-y:auto; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.2))); border-radius:8px; padding:8px;">
                  ${parts.map(p => {
                    const isChecked = preselectedPartIds.has(p.id);
                    const defQty = 1;
                    return `
                      <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; font-size:13px; padding:4px 0;">
                        <label style="display:flex; align-items:center; gap:6px; cursor:pointer; flex:1;">
                          <input type="checkbox" class="m-comp-part-cb" value="${p.id}" ${isChecked ? "checked" : ""}>
                          <span>${this._escape(p.name)} <span style="font-size:11px; color:var(--secondary-text-color, #64748b);">(Lager: ${p.stock} ${this._escape(p.unit || "")})</span></span>
                        </label>
                        <div style="display:flex; align-items:center; gap:4px;">
                          <input type="number" step="1" min="1" class="text-input m-comp-part-qty" data-part-id="${p.id}" value="${defQty}" style="width:60px; padding:4px 6px; font-size:12px;">
                          <span style="font-size:11px; color:var(--secondary-text-color, #64748b);">${this._escape(p.unit || "")}</span>
                        </div>
                      </div>
                    `;
                  }).join("")}
                </div>
              </div>
            ` : ""}

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">⏱️ ${this.t("durationMinutesLabel")}</label>
                <input type="number" class="text-input" id="m-comp-duration" value="${task.default_duration_minutes || ""}" placeholder="30">
              </div>
              <div class="form-group">
                <label class="form-label">💰 ${this.t("costLabel")}</label>
                <input type="number" step="0.01" class="text-input" id="m-comp-cost" value="${task.default_cost || ""}" placeholder="0.00">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">📅 ${this.t("completedAtLabel")}</label>
              <input type="datetime-local" class="text-input" id="m-comp-date" value="${nowIso}">
            </div>

            <div class="form-group">
              <label class="form-label">📝 ${this.t("notesLabel")}</label>
              <textarea class="text-input" id="m-comp-notes" rows="2" placeholder="${this.t("descriptionPlaceholder")}"></textarea>
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-submit-complete">✓ ${this.t("done")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderQrCodeModal() {
      const item = (this._modalState && this._modalState.item) || {};
      const itemType = (this._modalState && this._modalState.itemType) || "task";
      const isTask = itemType === "task";
      const targetUrl = this._getQrTargetUrl(item, itemType);
      const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
      
      let qrSvg = "";
      try {
        if (typeof QRCodeGen !== "undefined") {
          const qr = new QRCodeGen({
            content: targetUrl,
            width: 200,
            height: 200,
            padding: 1,
            container: "svg-viewbox",
            join: true
          });
          qrSvg = qr.svg();
        }
      } catch (e) {
        console.error("QR Code error:", e);
      }

      const title = this._escape(item.title || item.name || "");
      const subtitle = isTask ? this.t("qrTaskSubtitle") : this.t("qrThingSubtitle");

      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window" style="position:relative; text-align:center; max-width:440px;">
            <button class="modal-close-btn" title="${this.t("close")}">✕</button>
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 4px 0; font-size:18px;">
              📱 ${this.t("qrCode")}: ${title}
            </h2>
            <p style="font-size:12px; color:var(--secondary-text-color, #64748b); margin:0 0 16px 0;">
              ${subtitle}
            </p>

            ${isLocalhost ? `
              <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid #f59e0b; border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #b45309; margin-bottom: 14px; text-align: left; line-height: 1.4;">
                ⚠️ ${this.t("qrLocalhostWarning")}
              </div>
            ` : ""}

            <div id="qr-container" style="display:inline-block; background:#ffffff; padding:14px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.08); margin-bottom:14px;">
              ${qrSvg || `<div style="padding:40px; color:#64748b;">[QR Code]</div>`}
            </div>

            <div style="background:var(--secondary-background-color, rgba(127,127,127,0.08)); border-radius:8px; padding:8px 12px; font-family:monospace; font-size:11px; word-break:break-all; margin-bottom:16px; border:1px solid var(--ha-card-border-color, var(--divider-color, rgba(127,127,127,0.15))); text-align:left;">
              <div style="font-size:10px; font-weight:600; color:var(--secondary-text-color, #64748b); margin-bottom:2px; font-family:sans-serif;">${this.t("targetUrl")}:</div>
              <span id="qr-target-url-text">${this._escape(targetUrl)}</span>
            </div>

            <div style="display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; gap:8px; justify-content:center;">
                <button class="btn btn-secondary" id="btn-copy-qr-link" style="flex:1;">📋 ${this.t("copyLink")}</button>
                <button class="btn btn-secondary" id="btn-print-qr-tag" style="flex:1;">🖨️ ${this.t("printTag")}</button>
              </div>
              <button class="btn btn-primary" id="modal-cancel" style="width:100%;">✕ ${this.t("close")}</button>
            </div>
          </div>
        </div>
      `;
    }


    _renderUserModal() {
      const isGamification = this._data.settings && this._data.settings.gamification_enabled !== false;
      const user = this._modalState.user;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${user.id ? this.t("editUser") : this.t("addUser")}
            </h2>

            <div class="form-group">
              <label class="form-label">${this.t("memberNameLabel")}</label>
              <input type="text" class="text-input" id="m-user-name" value="${this._escape(user.name)}" placeholder="${this.t("memberNamePlaceholder")}">
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("colorTheme")}</label>
              <input type="color" id="m-user-color" value="${user.color || "#3b82f6"}" style="width:60px; height:36px; border:none; border-radius:6px; cursor:pointer;">
            </div>

            ${isGamification ? `
              <div class="form-group">
                <label class="form-label">${this.t("points")}</label>
                <input type="number" class="text-input" id="m-user-points" value="${user.points || 0}">
              </div>
            ` : `
              <input type="hidden" id="m-user-points" value="${user.points || 0}">
            `}

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-user">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    _renderLabelModal() {
      const label = this._modalState.label;
      return `
        <div class="modal-backdrop" id="modal-backdrop">
          <div class="modal-window">
            <div class="modal-handle"></div>
            <h2 style="margin:0 0 12px 0; font-size:18px;">
              ${label.id ? this.t("editLabel") : this.t("addLabel")}
            </h2>

            <div class="form-group">
              <label class="form-label">${this.t("labelNameLabel")}</label>
              <input type="text" class="text-input" id="m-label-name" value="${this._escape(label.name)}" placeholder="${this.t("labelNamePlaceholder")}">
            </div>

            <div class="form-group">
              <label class="form-label">${this.t("colorLabel")}</label>
              <input type="color" id="m-label-color" value="${label.color || "#10b981"}" style="width:60px; height:36px; border:none; border-radius:6px; cursor:pointer;">
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" id="modal-cancel">${this.t("cancel")}</button>
              <button class="btn btn-primary" id="modal-save-label">${this.t("save")}</button>
            </div>
          </div>
        </div>
      `;
    }

    // ================= EVENT ATTACHMENT =================
    _attachEventListeners() {
      const root = this.shadowRoot;

      // Hamburger Menu Toggle (opens/closes Home Assistant sidebar)
      const menuToggleBtn = root.getElementById("menu-toggle-btn");
      if (menuToggleBtn) {
        menuToggleBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const event = new CustomEvent("hass-toggle-menu", {
            bubbles: true,
            composed: true,
            detail: { open: true },
          });
          this.dispatchEvent(event);
          window.dispatchEvent(event);
          try {
            const ha = document.querySelector("home-assistant");
            const main = ha && ha.shadowRoot && ha.shadowRoot.querySelector("home-assistant-main");
            if (main) {
              main.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true, detail: { open: true } }));
            }
          } catch (err) {}
          if (window.parent && window.parent !== window) {
            try {
              window.parent.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true, detail: { open: true } }));
            } catch (err) {}
          }
        });
      }

      // Nav Tabs
      root.querySelectorAll(".nav-tab").forEach(tab => {
        tab.addEventListener("click", () => {
          this._currentTab = tab.getAttribute("data-tab");
          this._render();
        });
      });

      const btnGotoSettings = root.getElementById("btn-goto-settings-from-leaderboard");
      if (btnGotoSettings) {
        btnGotoSettings.addEventListener("click", () => {
          this._currentTab = "settings";
          this._render();
        });
      }

      // Filter pills
      root.querySelectorAll(".filter-pill").forEach(pill => {
        pill.addEventListener("click", () => {
          this._filterStatus = pill.getAttribute("data-status");
          this._render();
        });
      });

      // Search
      const searchInput = root.getElementById("search-input");
      if (searchInput) {
        searchInput.addEventListener("input", (e) => {
          this._searchQuery = e.target.value;
          this._render();
        });
      }

      // Assignee Filter
      const assigneeFilter = root.getElementById("filter-assignee");
      if (assigneeFilter) {
        assigneeFilter.addEventListener("change", (e) => {
          this._filterAssignee = e.target.value;
          this._render();
        });
      }

      // Label Filter
      const labelFilter = root.getElementById("filter-label");
      if (labelFilter) {
        labelFilter.addEventListener("change", (e) => {
          this._filterLabel = e.target.value;
          this._render();
        });
      }

      // Provider / List Filter
      const providerFilter = root.getElementById("filter-provider");
      if (providerFilter) {
        providerFilter.addEventListener("change", (e) => {
          this._filterProvider = e.target.value;
          this._render();
        });
      }

      // Active User Header Select
      const headerUserSelect = root.getElementById("header-user-select");
      if (headerUserSelect) {
        headerUserSelect.addEventListener("change", (e) => {
          this._activeUser = e.target.value;
          this._render();
        });
      }

      // Tablet / Mount Mode toggle
      const btnMount = root.getElementById("btn-toggle-mount");
      if (btnMount) {
        btnMount.addEventListener("click", () => {
          this._tabletMode = !this._tabletMode;
          if (this._tabletMode) {
            this.classList.add("tablet-mode");
          } else {
            this.classList.remove("tablet-mode");
          }
          this._render();
        });
      }

      // Add Task / Thing / Part Button
      const btnAddTask = root.getElementById("btn-add-task");
      if (btnAddTask) {
        btnAddTask.addEventListener("click", () => {
          if (this._currentTab === "things") {
            this.openThingModal();
          } else if (this._currentTab === "parts") {
            this.openPartModal();
          } else {
            this.openTaskModal();
          }
        });
      }

      // Empty State Add Task Button
      const btnEmptyAddTask = root.getElementById("btn-empty-add-task");
      if (btnEmptyAddTask) {
        btnEmptyAddTask.addEventListener("click", () => this.openTaskModal());
      }

      // Add Thing Button
      const btnAddThing = root.getElementById("btn-add-thing");
      if (btnAddThing) {
        btnAddThing.addEventListener("click", () => this.openThingModal());
      }

      // Empty State Add Thing Button
      const btnEmptyAddThing = root.getElementById("btn-empty-add-thing");
      if (btnEmptyAddThing) {
        btnEmptyAddThing.addEventListener("click", () => this.openThingModal());
      }

      // Mobile FAB
      const fabAddBtn = root.getElementById("fab-add-btn");
      if (fabAddBtn) {
        fabAddBtn.addEventListener("click", () => {
          if (this._currentTab === "things") {
            this.openThingModal();
          } else if (this._currentTab === "parts") {
            this.openPartModal();
          } else {
            this.openTaskModal();
          }
        });
      }

      // Add User Button
      const btnAddUser = root.getElementById("btn-add-user");
      if (btnAddUser) {
        btnAddUser.addEventListener("click", () => this.openUserModal());
      }

      // Add Label Button
      const btnAddLabel = root.getElementById("btn-add-label");
      if (btnAddLabel) {
        btnAddLabel.addEventListener("click", () => this.openLabelModal());
      }

      // Task complete toggle
      root.querySelectorAll("[data-complete-task]").forEach(btn => {
        btn.addEventListener("click", (e) => {
          const tId = btn.getAttribute("data-complete-task");
          const task = this._data.tasks.find(t => t.id === tId);
          if (task && task.status === "completed") {
            this.resetTask(tId);
          } else if (task && task.task_type === "reading") {
            this.openCompleteModal(task);
          } else {
            this.completeTask(tId);
          }
        });
      });

      // Complete with details
      root.querySelectorAll("[data-details-complete-task]").forEach(btn => {
        btn.addEventListener("click", () => {
          const tId = btn.getAttribute("data-details-complete-task");
          const task = this._data.tasks.find(t => t.id === tId);
          if (task) this.openCompleteModal(task);
        });
      });

      // Skip Task
      root.querySelectorAll("[data-skip-task]").forEach(btn => {
        btn.addEventListener("click", () => {
          const tId = btn.getAttribute("data-skip-task");
          this.skipTask(tId);
        });
      });

      // QR Code Task / Thing
      root.querySelectorAll("[data-qr-task]").forEach(btn => {
        btn.addEventListener("click", () => {
          const tId = btn.getAttribute("data-qr-task");
          const task = this._data.tasks.find(t => t.id === tId);
          if (task) this.openQrModal(task, "task");
        });
      });

      root.querySelectorAll("[data-qr-thing]").forEach(btn => {
        btn.addEventListener("click", () => {
          const thId = btn.getAttribute("data-qr-thing");
          const thing = (this._data.things || []).find(t => t.id === thId);
          if (thing) this.openQrModal(thing, "thing");
        });
      });

      // Parts Shelf Actions
      const btnAddPart = root.getElementById("btn-add-part");
      if (btnAddPart) btnAddPart.addEventListener("click", () => this.openPartModal());
      const btnEmptyAddPart = root.getElementById("btn-empty-add-part");
      if (btnEmptyAddPart) btnEmptyAddPart.addEventListener("click", () => this.openPartModal());

      root.querySelectorAll("[data-edit-part]").forEach(btn => {
        btn.addEventListener("click", () => {
          const p = (this._data.parts || []).find(x => x.id === btn.getAttribute("data-edit-part"));
          if (p) this.openPartModal(p);
        });
      });

      root.querySelectorAll("[data-delete-part]").forEach(btn => {
        btn.addEventListener("click", () => this.deletePart(btn.getAttribute("data-delete-part")));
      });

      root.querySelectorAll("[data-part-adjust]").forEach(btn => {
        btn.addEventListener("click", () => {
          const pId = btn.getAttribute("data-part-adjust");
          const delta = parseFloat(btn.getAttribute("data-delta"));
          this.adjustPartStock(pId, delta);
        });
      });

      // Task Subtask Toggle
      root.querySelectorAll("[data-subtask-task]").forEach(cb => {
        cb.addEventListener("change", (e) => {
          const tId = cb.getAttribute("data-subtask-task");
          const stId = cb.getAttribute("data-subtask-id");
          this.toggleSubtask(tId, stId, !cb.checked);
        });
      });

      // Task Edit / Delete
      root.querySelectorAll("[data-edit-task]").forEach(btn => {
        btn.addEventListener("click", () => {
          const t = this._data.tasks.find(x => x.id === btn.getAttribute("data-edit-task"));
          if (t) this.openTaskModal(t);
        });
      });

      root.querySelectorAll("[data-delete-task]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteTask(btn.getAttribute("data-delete-task")));
      });

      root.querySelectorAll("[data-duplicate-task]").forEach(btn => {
        btn.addEventListener("click", () => this.duplicateTask(btn.getAttribute("data-duplicate-task")));
      });

      // Task Active / Pause Toggle
      root.querySelectorAll("[data-toggle-active-task]").forEach(btn => {
        btn.addEventListener("click", async () => {
          const tId = btn.getAttribute("data-toggle-active-task");
          const task = (this._data.tasks || []).find(t => t.id === tId);
          if (task) {
            if (task.is_active === false) {
              await this.resumeTask(tId);
            } else {
              await this.pauseTask(tId);
            }
          }
        });
      });

      // Thing actions
      root.querySelectorAll("[data-thing-delta]").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-thing-delta");
          const delta = parseFloat(btn.getAttribute("data-delta"));
          this.updateThingValue(id, delta);
        });
      });

      root.querySelectorAll("[data-thing-reset]").forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-thing-reset");
          this.updateThingValue(id, null, true);
        });
      });

      root.querySelectorAll("[data-edit-thing]").forEach(btn => {
        btn.addEventListener("click", () => {
          const th = this._data.things.find(x => x.id === btn.getAttribute("data-edit-thing"));
          if (th) this.openThingModal(th);
        });
      });

      root.querySelectorAll("[data-delete-thing]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteThing(btn.getAttribute("data-delete-thing")));
      });

      // User actions
      root.querySelectorAll("[data-edit-user]").forEach(btn => {
        btn.addEventListener("click", () => {
          const u = this._data.users.find(x => x.id === btn.getAttribute("data-edit-user"));
          if (u) this.openUserModal(u);
        });
      });

      root.querySelectorAll("[data-delete-user]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteUser(btn.getAttribute("data-delete-user")));
      });

      // Label actions
      root.querySelectorAll("[data-edit-label]").forEach(btn => {
        btn.addEventListener("click", () => {
          const l = this._data.labels.find(x => x.id === btn.getAttribute("data-edit-label"));
          if (l) this.openLabelModal(l);
        });
      });

      root.querySelectorAll("[data-delete-label]").forEach(btn => {
        btn.addEventListener("click", () => this.deleteLabel(btn.getAttribute("data-delete-label")));
      });

      // Calendar controls
      const calPrev = root.getElementById("cal-prev");
      if (calPrev) {
        calPrev.addEventListener("click", () => {
          this._calendarDate.setMonth(this._calendarDate.getMonth() - 1);
          this._render();
        });
      }
      const calNext = root.getElementById("cal-next");
      if (calNext) {
        calNext.addEventListener("click", () => {
          this._calendarDate.setMonth(this._calendarDate.getMonth() + 1);
          this._render();
        });
      }
      const calToday = root.getElementById("cal-today");
      if (calToday) {
        calToday.addEventListener("click", () => {
          this._calendarDate = new Date();
          this._calendarSelectedDay = new Date().toISOString().slice(0, 10);
          this._render();
        });
      }
      root.querySelectorAll("[data-cal-date]").forEach(cell => {
        cell.addEventListener("click", () => {
          this._calendarSelectedDay = cell.getAttribute("data-cal-date");
          this._render();
        });
      });

      // Backup & Settings
      const btnExport = root.getElementById("btn-export-backup");
      if (btnExport) btnExport.addEventListener("click", () => this._exportBackup());

      const inputImport = root.getElementById("input-import-backup");
      if (inputImport) {
        inputImport.addEventListener("change", (e) => this._importBackup(e.target));
      }

      const prefGamification = root.getElementById("pref-gamification");
      if (prefGamification) {
        prefGamification.addEventListener("change", (e) => {
          const group = root.getElementById("pref-default-points-group");
          if (group) group.style.display = e.target.checked ? "flex" : "none";
        });
      }

      const btnSavePrefs = root.getElementById("btn-save-prefs");
      if (btnSavePrefs) {
        btnSavePrefs.addEventListener("click", async () => {
          const newPrefs = {
            gamification_enabled: root.getElementById("pref-gamification").checked,
            sound_enabled: root.getElementById("pref-sounds").checked,
            confetti_enabled: root.getElementById("pref-confetti").checked,
            default_points: parseInt(root.getElementById("pref-default-points").value, 10) || 10,
            language: root.getElementById("pref-language") ? root.getElementById("pref-language").value : "auto"
          };
          await this._callWS("task_manager/update_settings", { settings: newPrefs });
          alert(this.t("prefSaved"));
        });
      }

      // External Providers buttons
      const btnSyncProv = root.getElementById("btn-sync-providers");
      if (btnSyncProv) {
        btnSyncProv.addEventListener("click", () => this.syncProviders());
      }

      const btnLinkProv = root.getElementById("btn-link-provider");
      if (btnLinkProv) {
        btnLinkProv.addEventListener("click", () => this.openLinkProviderModal());
      }

      root.querySelectorAll("[data-unlink-provider]").forEach(btn => {
        btn.addEventListener("click", () => {
          this.unlinkProvider(btn.getAttribute("data-unlink-provider"));
        });
      });

      // Modal Events
      const modalCancel = root.getElementById("modal-cancel");
      if (modalCancel) modalCancel.addEventListener("click", () => this.closeModal());

      const modalBackdrop = root.getElementById("modal-backdrop");
      if (modalBackdrop) {
        modalBackdrop.addEventListener("click", (e) => {
          if (e.target === modalBackdrop) this.closeModal();
        });
      }

      // Toggle manual vs dropdown in provider modal
      const btnToggleManual = root.getElementById("btn-toggle-manual-provider");
      if (btnToggleManual) {
        btnToggleManual.addEventListener("click", (e) => {
          e.preventDefault();
          if (this._modalState && this._modalState.type === "link_provider") {
            this._modalState.manualMode = !this._modalState.manualMode;
            this._render();
          }
        });
      }

      // Modal Save Provider
      const btnSaveProvider = root.getElementById("modal-save-provider");
      if (btnSaveProvider) {
        btnSaveProvider.addEventListener("click", async () => {
          const manualInput = root.getElementById("m-provider-entity-manual");
          const entitySelect = root.getElementById("m-provider-entity");
          let entityId = "";
          if (manualInput && manualInput.value.trim()) {
            entityId = manualInput.value.trim();
          } else if (entitySelect && entitySelect.value) {
            entityId = entitySelect.value;
          }
          if (!entityId) {
            alert(this.t("selectOrEnterEntity"));
            return;
          }
          if (!entityId.startsWith("todo.")) {
            alert(this.t("mustStartWithTodo"));
            return;
          }
          const nameInput = root.getElementById("m-provider-name");
          const customName = nameInput ? nameInput.value.trim() : "";
          await this.linkProvider(entityId, customName);
        });
      }

      // Modal Save Task
      const btnSaveTask = root.getElementById("modal-save-task");
      if (btnSaveTask) {
        btnSaveTask.addEventListener("click", async () => {
          const title = root.getElementById("m-task-title").value.trim();
          if (!title) {
            alert(this.t("titleRequired"));
            return;
          }
          const recEnabled = root.getElementById("m-task-rec-enable").checked;
          const subtaskInputs = root.querySelectorAll(".m-subtask-input");
          const subtasks = Array.from(subtaskInputs).map(inp => inp.value.trim()).filter(Boolean);

          const assignee = root.getElementById("m-task-assignee").value;
          const destSelect = root.getElementById("m-task-dest");
          const destProvider = destSelect ? destSelect.value : undefined;
          const selectedReminders = Array.from(root.querySelectorAll(".m-reminder-checkbox:checked")).map(cb => parseInt(cb.value, 10));
          const selectedWeekdays = Array.from(root.querySelectorAll(".m-weekday-checkbox:checked")).map(cb => parseInt(cb.value, 10));

          const tagsStr = root.getElementById("m-task-tags") ? root.getElementById("m-task-tags").value.trim() : "";
          const tags = tagsStr ? tagsStr.split(",").map(t => t.trim()).filter(Boolean) : [];

          const depSelect = root.getElementById("m-task-dependencies");
          const dependencies = depSelect ? Array.from(depSelect.selectedOptions).map(o => o.value) : [];

          const recMode = root.getElementById("m-task-rec-mode") ? root.getElementById("m-task-rec-mode").value : "after";
          const recEveryType = root.getElementById("m-task-rec-every-type") ? root.getElementById("m-task-rec-every-type").value : "repeat_every_weekday";
          const recEveryWeekday = parseInt(root.getElementById("m-task-every-weekday") ? root.getElementById("m-task-every-weekday").value : "0", 10);
          const recEveryDay = parseInt(root.getElementById("m-task-every-day") ? root.getElementById("m-task-every-day").value : "1", 10);
          const recEveryNth = parseInt(root.getElementById("m-task-every-nth") ? root.getElementById("m-task-every-nth").value : "1", 10);
          const recEveryNthWeekday = parseInt(root.getElementById("m-task-every-nth-weekday") ? root.getElementById("m-task-every-nth-weekday").value : "0", 10);
          const recEveryDaysBefore = parseInt(root.getElementById("m-task-every-days-before") ? root.getElementById("m-task-every-days-before").value : "1", 10);

          const taskType = root.getElementById("m-task-type") ? root.getElementById("m-task-type").value : "chore";
          const readingUnit = root.getElementById("m-task-reading-unit") ? root.getElementById("m-task-reading-unit").value.trim() : "";
          const durMin = root.getElementById("m-task-duration") ? parseInt(root.getElementById("m-task-duration").value, 10) || 0 : 0;
          const defCost = root.getElementById("m-task-cost") ? parseFloat(root.getElementById("m-task-cost").value) || 0.0 : 0.0;
          const onCompleteEnt = root.getElementById("m-task-on-complete-entity") ? root.getElementById("m-task-on-complete-entity").value.trim() || null : null;

          const taskPayload = {
            id: this._modalState.task.id || undefined,
            title: title,
            description: root.getElementById("m-task-desc").value.trim(),
            due_date: root.getElementById("m-task-date").value,
            due_time: root.getElementById("m-task-time").value,
            priority: root.getElementById("m-task-priority").value,
            points: parseInt(root.getElementById("m-task-points").value, 10) || 10,
            assignees: assignee ? [assignee] : [],
            current_assignee: assignee || null,
            rotation_mode: root.getElementById("m-task-rotation").value,
            destination_provider: destProvider,
            reminders: selectedReminders,
            is_active: root.getElementById("m-task-is-active") ? root.getElementById("m-task-is-active").checked : true,
            tags: tags,
            dependencies: dependencies,
            due_soon_days: parseInt(root.getElementById("m-task-due-soon-days").value, 10) || 0,
            notification_interval: parseInt(root.getElementById("m-task-notification-interval").value, 10) || 1,
            active_override: root.getElementById("m-task-active-override") ? root.getElementById("m-task-active-override").value.trim() || null : null,
            task_interval_override: root.getElementById("m-task-interval-override") ? root.getElementById("m-task-interval-override").value.trim() || null : null,
            due_soon_override: root.getElementById("m-task-due-soon-override") ? root.getElementById("m-task-due-soon-override").value.trim() || null : null,
            task_type: taskType,
            reading_unit: readingUnit,
            default_duration_minutes: durMin,
            default_cost: defCost,
            on_complete_entity_id: onCompleteEnt,
            recurrence: {
              enabled: recEnabled,
              repeat_mode: recMode,
              type: root.getElementById("m-task-rec-type") ? root.getElementById("m-task-rec-type").value : "none",
              interval: parseInt(root.getElementById("m-task-rec-interval") ? root.getElementById("m-task-rec-interval").value : "1", 10),
              based_on: root.getElementById("m-task-rec-based") ? root.getElementById("m-task-rec-based").value : "due_date",
              weekdays: selectedWeekdays,
              repeat_every_type: recEveryType,
              repeat_every_weekday: recEveryType === "repeat_every_weekday_of_month" ? recEveryNthWeekday : recEveryWeekday,
              repeat_every_day_of_month: recEveryDay,
              repeat_every_weekday_of_month: recEveryType === "repeat_every_weekday_of_month",
              repeat_every_nth: recEveryNth,
              repeat_every_days_before_end_of_month: recEveryDaysBefore
            },
            subtasks: subtasks,
            linked_thing_id: root.getElementById("m-task-linked-thing").value || null,
            thing_action: "reset"
          };

          await this._callWS("task_manager/save_task", { task: taskPayload });
          this.closeModal();
        });
      }

      // Modal Pause/Resume Toggle
      const btnPauseToggle = root.getElementById("m-task-btn-pause-toggle");
      const chkActive = root.getElementById("m-task-is-active");
      if (btnPauseToggle) {
        btnPauseToggle.addEventListener("click", async () => {
          if (!this._modalState || !this._modalState.task) return;
          const tId = this._modalState.task.id;
          const isCurrentlyActive = this._modalState.task.is_active !== false;
          if (isCurrentlyActive) {
            await this.pauseTask(tId);
            this._modalState.task.is_active = false;
          } else {
            await this.resumeTask(tId);
            this._modalState.task.is_active = true;
          }
          if (chkActive) chkActive.checked = this._modalState.task.is_active;
          const statusText = root.getElementById("m-task-status-text");
          if (statusText) {
            statusText.innerText = this._modalState.task.is_active ? `✅ ${this.t("isActive")}` : `⏸️ ${this.t("isPaused")}`;
          }
          btnPauseToggle.innerHTML = this._modalState.task.is_active ? `⏸️ ${this.t("pauseTask")}` : `▶️ ${this.t("resumeTask")}`;
        });
      }
      if (chkActive) {
        chkActive.addEventListener("change", (e) => {
          const statusText = root.getElementById("m-task-status-text");
          if (statusText) {
            statusText.innerText = e.target.checked ? `✅ ${this.t("isActive")}` : `⏸️ ${this.t("isPaused")}`;
          }
          if (btnPauseToggle) {
            btnPauseToggle.innerHTML = e.target.checked ? `⏸️ ${this.t("pauseTask")}` : `▶️ ${this.t("resumeTask")}`;
          }
        });
      }

      // Modal Task Type Change
      const mTaskType = root.getElementById("m-task-type");
      if (mTaskType) {
        mTaskType.addEventListener("change", (e) => {
          const grp = root.getElementById("m-task-reading-unit-group");
          if (grp) grp.style.display = e.target.value === "reading" ? "block" : "none";
        });
      }

      // Modal Recurrence Toggle
      const mRecEnable = root.getElementById("m-task-rec-enable");
      if (mRecEnable) {
        mRecEnable.addEventListener("change", (e) => {
          const f = root.getElementById("m-rec-fields");
          if (f) f.style.display = e.target.checked ? "flex" : "none";
        });
      }

      // Modal Recurrence Mode Toggle (After vs Every)
      const mRecMode = root.getElementById("m-task-rec-mode");
      if (mRecMode) {
        mRecMode.addEventListener("change", (e) => {
          const modeAfter = root.getElementById("m-rec-mode-after");
          const modeEvery = root.getElementById("m-rec-mode-every");
          if (modeAfter) modeAfter.style.display = e.target.value === "after" ? "grid" : "none";
          if (modeEvery) modeEvery.style.display = e.target.value === "every" ? "flex" : "none";
        });
      }

      // Modal Recurrence Every Subtype Change
      const mRecEveryType = root.getElementById("m-task-rec-every-type");
      if (mRecEveryType) {
        mRecEveryType.addEventListener("change", (e) => {
          const val = e.target.value;
          const grpWd = root.getElementById("m-every-weekday-group");
          const grpDay = root.getElementById("m-every-day-group");
          const grpNth = root.getElementById("m-every-weekday-month-group");
          const grpBef = root.getElementById("m-every-days-before-group");
          if (grpWd) grpWd.style.display = val === "repeat_every_weekday" ? "block" : "none";
          if (grpDay) grpDay.style.display = val === "repeat_every_day_of_month" ? "block" : "none";
          if (grpNth) grpNth.style.display = val === "repeat_every_weekday_of_month" ? "grid" : "none";
          if (grpBef) grpBef.style.display = val === "repeat_every_days_before_end_of_month" ? "block" : "none";
        });
      }

      // Modal Recurrence Type Change (Show/Hide Weekdays)
      const mRecType = root.getElementById("m-task-rec-type");
      if (mRecType) {
        mRecType.addEventListener("change", (e) => {
          const wd = root.getElementById("m-rec-weekdays");
          if (wd) wd.style.display = e.target.value === "weekly" ? "block" : "none";
        });
      }

      // Modal Add Subtask Row
      const btnAddSubtaskRow = root.getElementById("btn-add-subtask-row");
      if (btnAddSubtaskRow) {
        btnAddSubtaskRow.addEventListener("click", () => {
          const container = root.getElementById("subtasks-container");
          const div = document.createElement("div");
          div.style.cssText = "display:flex; gap:6px;";
          div.innerHTML = `
            <input type="text" class="text-input m-subtask-input" placeholder="${this.t("newSubtaskPlaceholder")}" style="flex:1;">
            <button class="btn btn-secondary btn-del-subtask">×</button>
          `;
          div.querySelector(".btn-del-subtask").addEventListener("click", () => div.remove());
          container.appendChild(div);
        });
      }

      root.querySelectorAll(".btn-del-subtask").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.target.parentElement.remove();
        });
      });

      // Modal Linked Thing Change (Show Hint)
      const mLinkedThing = root.getElementById("m-task-linked-thing");
      if (mLinkedThing) {
        mLinkedThing.addEventListener("change", (e) => {
          const hint = root.getElementById("m-task-thing-hint");
          if (hint) hint.style.display = e.target.value ? "block" : "none";
        });
      }

      // Modal External Entity and Script Pickers for Thing
      this._setupEntityPicker({
        inputId: "m-thing-external-entity",
        clearBtnId: "m-thing-external-entity-clear",
        dropdownId: "m-thing-external-entity-dropdown",
        getEntities: () => this._availableNumericEntities || this._getNumericEntities(),
        onSelect: (ent) => {
          if (ent) {
            this._applyNumericEntityAutoFill(ent);
          }
        },
        renderBadge: (ent) => {
          if (ent && ent.state !== undefined && ent.state !== null && ent.state !== "") {
            return `<div class="entity-dropdown-badge">${this._escape(String(ent.state))} ${this._escape(ent.unit || "")}</div>`;
          }
          return "";
        }
      });

      this._setupEntityPicker({
        inputId: "m-thing-script",
        clearBtnId: "m-thing-script-clear",
        dropdownId: "m-thing-script-dropdown",
        getEntities: () => this._availableScriptEntities || this._getScriptEntities(),
        onSelect: null,
        renderBadge: () => `<div class="entity-dropdown-badge" style="background:#f5f3ff; color:#7c3aed;">script</div>`
      });

      // Modal Save Thing
      const btnSaveThing = root.getElementById("modal-save-thing");
      if (btnSaveThing) {
        btnSaveThing.addEventListener("click", async () => {
          const name = root.getElementById("m-thing-name").value.trim();
          if (!name) {
            alert(this.t("nameRequired"));
            return;
          }
          const curVal = parseFloat(root.getElementById("m-thing-current").value);
          const targetVal = parseFloat(root.getElementById("m-thing-target").value);
          const operator = root.getElementById("m-thing-operator") ? root.getElementById("m-thing-operator").value : ">=";
          const extEntity = root.getElementById("m-thing-external-entity") ? root.getElementById("m-thing-external-entity").value.trim() || null : null;

          const manufacturer = root.getElementById("m-thing-manufacturer") ? root.getElementById("m-thing-manufacturer").value.trim() : "";
          const model = root.getElementById("m-thing-model") ? root.getElementById("m-thing-model").value.trim() : "";
          const serialNum = root.getElementById("m-thing-serial") ? root.getElementById("m-thing-serial").value.trim() : "";
          const installDate = root.getElementById("m-thing-install-date") ? root.getElementById("m-thing-install-date").value : "";
          const warrantyExp = root.getElementById("m-thing-warranty-expiry") ? root.getElementById("m-thing-warranty-expiry").value : "";
          const docUrl = root.getElementById("m-thing-doc-url") ? root.getElementById("m-thing-doc-url").value.trim() : "";

          const thingPayload = {
            id: this._modalState.thing.id || undefined,
            name: name,
            category: root.getElementById("m-thing-category").value.trim(),
            unit: root.getElementById("m-thing-unit").value.trim(),
            current_value: isNaN(curVal) ? 0 : curVal,
            target_value: isNaN(targetVal) ? 0 : targetVal,
            threshold_operator: operator,
            external_entity_id: extEntity,
            script_entity_id: root.getElementById("m-thing-script") ? root.getElementById("m-thing-script").value.trim() || null : null,
            manufacturer: manufacturer,
            model: model,
            serial_number: serialNum,
            installation_date: installDate,
            warranty_expiry: warrantyExp,
            documentation_url: docUrl,
            auto_task_creation: false,
            auto_task_title: ""
          };

          await this._callWS("task_manager/save_thing", { thing: thingPayload });
          this.closeModal();
        });
      }

      
      // Modal Save Part
      const btnSavePart = root.getElementById("modal-save-part");
      if (btnSavePart) {
        btnSavePart.addEventListener("click", async () => {
          const name = root.getElementById("m-part-name").value.trim();
          if (!name) {
            alert(this.t("titleRequired"));
            return;
          }
          const stock = parseFloat(root.getElementById("m-part-stock").value) || 0;
          const minStock = parseFloat(root.getElementById("m-part-min-stock").value) || 0;
          const unitPrice = parseFloat(root.getElementById("m-part-unit-price").value) || 0;

          const partPayload = {
            id: (this._modalState.part && this._modalState.part.id) || undefined,
            name: name,
            part_number: root.getElementById("m-part-number").value.trim(),
            thing_id: root.getElementById("m-part-thing-id").value || null,
            stock: stock,
            min_stock: minStock,
            unit: root.getElementById("m-part-unit").value.trim() || "pcs",
            unit_price: unitPrice,
            storage_location: root.getElementById("m-part-location").value.trim(),
            reorder_url: root.getElementById("m-part-reorder-url").value.trim(),
            notes: root.getElementById("m-part-notes").value.trim()
          };

          await this.savePart(partPayload);
        });
      }

      // Modal Submit Complete Details
      const btnSubmitComplete = root.getElementById("modal-submit-complete");
      if (btnSubmitComplete) {
        btnSubmitComplete.addEventListener("click", async () => {
          const task = this._modalState.task;
          if (!task) return;

          const readingInput = root.getElementById("m-comp-reading");
          const readingVal = readingInput ? readingInput.value.trim() : null;

          const consumedParts = [];
          root.querySelectorAll(".m-comp-part-cb:checked").forEach(cb => {
            const pId = cb.value;
            const qtyInput = root.querySelector(`.m-comp-part-qty[data-part-id="${pId}"]`);
            const qty = qtyInput ? parseFloat(qtyInput.value) || 1 : 1;
            consumedParts.push({ part_id: pId, quantity: qty });
          });

          const dur = root.getElementById("m-comp-duration") ? root.getElementById("m-comp-duration").value : null;
          const cost = root.getElementById("m-comp-cost") ? root.getElementById("m-comp-cost").value : null;
          const notes = root.getElementById("m-comp-notes") ? root.getElementById("m-comp-notes").value.trim() : null;
          const compDate = root.getElementById("m-comp-date") ? root.getElementById("m-comp-date").value : null;

          await this.completeTask(task.id, {
            reading_value: readingVal,
            consumed_parts: consumedParts,
            duration_minutes: dur,
            cost: cost,
            notes: notes,
            completed_at: compDate ? new Date(compDate).toISOString() : null
          });
        });
      }

      // Live reading delta preview in complete modal
      const mCompReading = root.getElementById("m-comp-reading");
      if (mCompReading && this._modalState && this._modalState.task) {
        const lastVal = this._modalState.task.last_reading_value;
        const unit = this._modalState.task.reading_unit || "";
        mCompReading.addEventListener("input", (e) => {
          const deltaEl = root.getElementById("m-comp-reading-delta");
          if (!deltaEl) return;
          const curVal = parseFloat(e.target.value);
          if (!isNaN(curVal) && lastVal !== undefined && lastVal !== null && !isNaN(parseFloat(lastVal))) {
            const diff = curVal - parseFloat(lastVal);
            deltaEl.textContent = `${this.t("consumptionDelta")}: ${diff >= 0 ? "+" : ""}${diff.toFixed(2)} ${unit}`;
          } else {
            deltaEl.textContent = "";
          }
        });
      }

      // Close button on modals
      root.querySelectorAll(".modal-close-btn").forEach(btn => {
        btn.addEventListener("click", () => this.closeModal());
      });

      // Copy QR Link
      const btnCopyQr = root.getElementById("btn-copy-qr-link");
      if (btnCopyQr) {
        btnCopyQr.addEventListener("click", async () => {
          const item = (this._modalState && this._modalState.item) || {};
          const itemType = (this._modalState && this._modalState.itemType) || "task";
          const targetUrl = this._getQrTargetUrl(item, itemType);

          const copied = await this._copyToClipboard(targetUrl);
          if (copied) {
            const originalHtml = btnCopyQr.innerHTML;
            btnCopyQr.innerHTML = `✓ ${this.t("linkCopied")}`;
            btnCopyQr.style.background = "var(--success-color, #10b981)";
            btnCopyQr.style.color = "#ffffff";
            this._showToast(`📋 ${this.t("linkCopied")}`);
            setTimeout(() => {
              btnCopyQr.innerHTML = originalHtml;
              btnCopyQr.style.background = "";
              btnCopyQr.style.color = "";
            }, 2500);
          }
        });
      }

      // Print QR Tag
      const btnPrintQr = root.getElementById("btn-print-qr-tag");
      if (btnPrintQr) {
        btnPrintQr.addEventListener("click", () => {
          const item = (this._modalState && this._modalState.item) || {};
          const itemType = (this._modalState && this._modalState.itemType) || "task";
          const targetUrl = this._getQrTargetUrl(item, itemType);

          const qrContainer = root.getElementById("qr-container");
          const qrSvg = qrContainer ? qrContainer.innerHTML : "";
          const title = item.title || item.name || "Task Manager";
          const subtitle = itemType === "thing" ? this.t("qrThingSubtitle") : this.t("qrTaskSubtitle");

          const origText = btnPrintQr.innerHTML;
          btnPrintQr.innerHTML = `🖨️ ${this.t("printTag")}...`;
          this._printTag(title, subtitle, qrSvg, targetUrl);
          setTimeout(() => {
            btnPrintQr.innerHTML = origText;
          }, 2000);
        });
      }

      // Modal Save User
      const btnSaveUser = root.getElementById("modal-save-user");
      if (btnSaveUser) {
        btnSaveUser.addEventListener("click", async () => {
          const name = root.getElementById("m-user-name").value.trim();
          if (!name) {
            alert(this.t("nameRequired"));
            return;
          }
          const userPayload = {
            id: this._modalState.user.id || undefined,
            name: name,
            color: root.getElementById("m-user-color").value,
            points: parseInt(root.getElementById("m-user-points").value, 10) || 0
          };

          await this._callWS("task_manager/save_user", { user: userPayload });
          this.closeModal();
        });
      }

      // Modal Save Label
      const btnSaveLabel = root.getElementById("modal-save-label");
      if (btnSaveLabel) {
        btnSaveLabel.addEventListener("click", async () => {
          const name = root.getElementById("m-label-name").value.trim();
          if (!name) {
            alert(this.t("nameRequired"));
            return;
          }
          const labelPayload = {
            id: this._modalState.label.id || undefined,
            name: name,
            color: root.getElementById("m-label-color").value
          };

          await this._callWS("task_manager/save_label", { label: labelPayload });
          this.closeModal();
        });
      }
    }

    _applyNumericEntityAutoFill(match) {
      if (!match) return;
      const root = this.shadowRoot;
      const nameEl = root.getElementById("m-thing-name");
      if (nameEl && !nameEl.value.trim() && match.name) nameEl.value = match.name;
      const unitEl = root.getElementById("m-thing-unit");
      if (unitEl && !unitEl.value.trim() && match.unit) unitEl.value = match.unit;
      const curEl = root.getElementById("m-thing-current");
      if (curEl && (!curEl.value || curEl.value === "0") && match.state !== undefined) {
        const parsed = parseFloat(match.state);
        curEl.value = !isNaN(parsed) ? parsed : match.state;
      }
      const opEl = root.getElementById("m-thing-operator");
      const targetEl = root.getElementById("m-thing-target");
      if (match.unit === "%" || /brush|filter|battery|life|rest/i.test(match.entity_id)) {
        if (opEl) opEl.value = "<=";
        if (targetEl && (!targetEl.value || targetEl.value === "30" || targetEl.value === "100")) targetEl.value = "0";
      }
    }

    _setupEntityPicker({ inputId, clearBtnId, dropdownId, getEntities, onSelect, renderBadge }) {
      const root = this.shadowRoot;
      const inputEl = root.getElementById(inputId);
      const clearBtnEl = root.getElementById(clearBtnId);
      const dropdownEl = root.getElementById(dropdownId);
      if (!inputEl || !dropdownEl) return;

      const filterAndRender = () => {
        const query = (inputEl.value || "").trim().toLowerCase();
        const allEntities = getEntities ? getEntities() : [];
        let filtered = allEntities;

        if (query) {
          filtered = allEntities.filter(e => {
            const eid = (e.entity_id || "").toLowerCase();
            const name = (e.name || "").toLowerCase();
            return eid.includes(query) || name.includes(query);
          });
          filtered.sort((a, b) => {
            const aName = (a.name || "").toLowerCase();
            const bName = (b.name || "").toLowerCase();
            const aId = (a.entity_id || "").toLowerCase();
            const bId = (b.entity_id || "").toLowerCase();
            const aStarts = aName.startsWith(query) || aId.startsWith(query);
            const bStarts = bName.startsWith(query) || bId.startsWith(query);
            if (aStarts && !bStarts) return -1;
            if (!aStarts && bStarts) return 1;
            return aName.localeCompare(bName);
          });
        }

        const maxDisplay = 50;
        const displayItems = filtered.slice(0, maxDisplay);

        if (displayItems.length === 0) {
          dropdownEl.innerHTML = `<div class="entity-dropdown-empty">${this.t("noMatchingEntities")}</div>`;
        } else {
          dropdownEl.innerHTML = displayItems.map(ent => `
            <div class="entity-dropdown-item ${inputEl.value.trim() === ent.entity_id ? "selected" : ""}" data-entity-id="${this._escape(ent.entity_id)}">
              <div style="min-width:0; flex:1;">
                <div class="entity-dropdown-name">${this._escape(ent.name || ent.entity_id)}</div>
                <div class="entity-dropdown-id">${this._escape(ent.entity_id)}</div>
              </div>
              ${renderBadge ? renderBadge(ent) : ""}
            </div>
          `).join("");

          dropdownEl.querySelectorAll(".entity-dropdown-item").forEach(item => {
            item.addEventListener("mousedown", (e) => {
              e.preventDefault();
              const entId = item.getAttribute("data-entity-id");
              const selectedEnt = allEntities.find(e => e.entity_id === entId) || { entity_id: entId, name: entId };
              inputEl.value = selectedEnt.entity_id;
              if (clearBtnEl) clearBtnEl.style.display = "flex";
              dropdownEl.style.display = "none";
              if (onSelect) onSelect(selectedEnt);
            });
          });
        }

        dropdownEl.style.display = "block";
      };

      // Prevent blur on input when scrolling or interacting with dropdown
      dropdownEl.addEventListener("mousedown", (e) => {
        if (!e.target.closest(".entity-dropdown-item")) {
          e.preventDefault();
        }
      });

      inputEl.addEventListener("input", () => {
        if (clearBtnEl) clearBtnEl.style.display = inputEl.value.trim() ? "flex" : "none";
        filterAndRender();
        const all = getEntities ? getEntities() : [];
        const match = all.find(e => e.entity_id.toLowerCase() === inputEl.value.trim().toLowerCase());
        if (match && onSelect) onSelect(match);
      });

      inputEl.addEventListener("focus", () => {
        filterAndRender();
      });

      inputEl.addEventListener("click", () => {
        if (dropdownEl.style.display === "none") {
          filterAndRender();
        }
      });

      inputEl.addEventListener("blur", () => {
        setTimeout(() => {
          dropdownEl.style.display = "none";
        }, 200);
      });

      inputEl.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          dropdownEl.style.display = "none";
        }
      });

      if (clearBtnEl) {
        clearBtnEl.addEventListener("mousedown", (e) => {
          e.preventDefault();
        });
        clearBtnEl.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          inputEl.value = "";
          clearBtnEl.style.display = "none";
          dropdownEl.style.display = "none";
          if (onSelect) onSelect(null);
          inputEl.focus();
        });
      }
    }

    _escape(text) {
      if (!text) return "";
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }
  }

  customElements.define("task-manager-panel", TaskManagerPanel);
  console.info("Task Manager sidebar panel registered successfully");
})();
