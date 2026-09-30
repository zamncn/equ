/* i18n.js — lightweight EN/ZH switcher for the static EquipSupply site.
 * Strategy: each leaf text node is translated by (1) its own data-zh attribute,
 * (2) the DICT map (exact textContent match), or (3) simple patterns.
 * No build step, GitHub-Pages friendly. Default language is English.
 */
(function () {
  'use strict';

  // English (key) -> Chinese (value). Keys must match the element's textContent exactly.
  var DICT = {
    // --- Navbar / megamenu ---
    'Home': '首页', 'Pages': '页面', 'Pages 1': '页面一', 'Pages 2': '页面二',
    'Pages 3': '页面三', 'Pages 4': '页面四', 'Typography': '排版', 'Buttons': '按钮',
    'Timers & Counters': '计时器与计数器', 'Forms': '表单', 'Grid system': '栅格系统',
    'Icon Lists': '图标列表', 'Privacy policy': '隐私政策', 'Privacy Policy': '隐私政策',
    'Coming Soon': '敬请期待', 'Search results': '搜索结果', 'Blog Post': '博客文章',
    'News': '新闻', 'News 2': '新闻二', 'About Us': '关于我们', 'Gallery': '产品图库',
    'Industries': '行业领域', 'Equipment': '设备中心', 'Product Page': '产品详情',
    'Contacts': '联系我们',
    // --- Navbar product families (mega menu) ---
    'Heavy Trucks': '重卡', 'Semi-Trailers': '半挂车',
    'Construction Machinery': '工程机械',
    // --- Footer / generic UI ---
    'share': '分享', 'Our Contacts': '联系方式', 'E-mail': '电子邮箱', 'Subscribe': '订阅',
    'Ph.': '电话', 'All Rights Reserved.': '版权所有', 'Loading...': '加载中…',
    'Get in touch': '联系我们',
    // --- Home page ---
    'high quality': '高品质', 'Reliable products': '可靠产品', 'Best service': '优质服务',
    'Equipment Rental': '设备租赁', 'Welcome to EquipSupply': '欢迎来到 EquipSupply',
    'Construction equipment': '工程机械', 'Browse by Industry': '按行业浏览',
    'Making your work safe': '让作业更安全', 'Qualified team': '专业团队',
    'Always honest & dedicated': '始终诚实奉献', 'Safety': '安全', 'Teamwork': '团队合作',
    'Integrity': '诚信', 'Our Products': '我们的产品',
    'Have questions? we can help': '有问题？我们随时为您服务',
    'View the full catalog': '查看完整目录', 'Latest News': '最新资讯',
    'Testimonials': '客户评价', 'Brands': '品牌', 'Order now': '立即订购',
    'Agriculture': '农业', 'Construction': '建筑工程', 'Mining': '采矿',
    'Transportation': '运输物流', 'Warehousing': '仓储', 'Asphalt Paving': '沥青摊铺',
    // --- About us ---
    'Who we are': '我们是谁', 'Why choose Us': '为何选择我们', 'Our Team': '我们的团队',
    'Dedication': '尽心尽责', 'Experience': '丰富经验', 'Professionalism': '专业素养',
    'Employees': '员工', 'Products': '产品', 'Clients': '客户', 'Partners': '合作伙伴',
    // --- Product category pages ---
    'All Products': '全部产品', 'View all': '查看全部',
    'Dump Trucks': '自卸车', 'Tractor Trucks': '牵引车', 'Special Trucks': '专用车',
    'Dump Truck': '自卸车', 'Tractor Truck': '牵引车', 'Special Truck': '专用车',
    'Semi-Trailer': '半挂车', 'Construction Machinery': '工程机械',
    'Concrete Mixer Truck': '混凝土搅拌车', 'Water Tank Truck': '洒水车',
    'Fuel Tanker Truck': '油罐车', 'Crane Truck': '起重车',
    'Boom Pump Truck': '泵车', 'Road Roller': '压路机', 'Forklift': '叉车',
    'Excavator': '挖掘机', 'Backhoe Loader': '挖掘装载机', 'Bulldozer': '推土机',
    'Truck Crane': '汽车起重机',
    'Fence Semi-Trailer': '仓栏半挂车', 'Low Flatbed Semi-Trailer': '低平板半挂车',
    'Dump Semi-Trailer': '自卸半挂车', 'Flatbed Semi-Trailer': '平板半挂车',
    'Curtain-side Semi-Trailer': '侧帘半挂车', 'Skeleton Semi-Trailer': '骨架半挂车',
    'Car Carrier Semi-Trailer': '轿运半挂车', 'Bulk Cement Semi-Trailer': '粉罐半挂车',
    'All Semi-Trailers': '全部半挂车', 'All Construction Machinery': '全部工程机械',
    // --- Agriculture Machinery ---
    'Agriculture Machinery': '农业机械',
    'All Agriculture Machinery': '全部农业机械',
    'Tractor': '拖拉机', 'Harvester': '收割机',
    'Seeding & Tillage Implements': '播种与耕整机具', 'Farm Transport & Others': '农用运输及其他',
    'Farm Tractor 40-80 hp': '农用拖拉机 40-80马力',
    'Farm Tractor 90-150 hp': '农用拖拉机 90-150马力',
    'Crawler Tractor': '履带拖拉机',
    'Wheel Combine Harvester': '轮式联合收割机',
    'Crawler Combine Harvester': '履带式联合收割机',
    'Corn Harvester': '玉米收获机',
    'Rotary Tiller': '旋耕机', 'Precision Seeder': '精量播种机',
    'Farm Dump Trailer': '农用自卸挂车', 'Agricultural Sprayer': '植保喷雾机',
    'Rated power': '额定功率', 'Drive type': '驱动型式', 'PTO speed': '动力输出转速',
    'Lifting capacity': '提升力', 'Gearbox': '变速箱', 'Track width': '履带宽度',
    'Ground pressure': '接地比压', 'Cutting width': '割幅', 'Grain tank': '粮箱容积',
    'Working efficiency': '作业效率', 'Rows': '行数', 'Row spacing': '行距',
    'Working width': '工作幅宽', 'Working depth': '耕深', 'Blade type': '刀片型式',
    'Matched power': '配套动力', 'Fertilizer box': '肥箱容积', 'Box volume': '货箱容积',
    'Tipping type': '卸料方式', 'Boom width': '喷幅', 'Pump flow': '泵流量',
    'Our company provides the most reliable heavy-duty equipment.': '我们提供最可靠的重型设备。',
    'Our team': '我们的团队',
    'CEO, founder': '创始人兼首席执行官', 'Chief financial officer': '首席财务官',
    'Head of Sales': '销售总监', 'Head of maintenance': '维修主管',
    'HR Manager': '人力资源经理', 'lead technician': '首席技术员',
    // --- Contacts ---
    'You can call us anytime': '您可随时来电咨询',
    'Feel free to email us your questions': '欢迎邮件咨询您的问题',
    'Contact Form': '联系表单', 'Your Name': '您的姓名', 'Phone': '电话',
    'Message': '留言', 'Send': '发送',
    // --- News ---
    'Tips': '贴士', 'Categories': '分类', 'news': '新闻', 'Newsletter': '订阅资讯',
    'Enter Your E-mail': '输入您的邮箱', 'Search': '搜索', 'Search News': '搜索资讯',
    'Related Posts': '相关文章', 'equipment': '设备', 'tips': '贴士',
    // --- Blog ---
    'Share post': '分享文章',
    // --- Privacy policy (section titles; body is placeholder Lorem, kept EN) ---
    'General information': '基本信息', 'Information We Collect': '我们收集的信息',
    'How We Use Your Information': '信息使用方式', 'Management of personal data': '个人数据管理',
    'Right to access, correct and delete data and to object to data processing':
      '访问、更正、删除数据及反对处理的权利', 'Sharing Your Information': '信息共享',
    // --- Product detail page ---
    'DT899-19 Dump Truck': 'DT899-19 自卸车', 'Engine Speed': '发动机转速',
    'Capacity': '额定容量', '2200 rpm': '2200 转/分', '21.7 cu. yd.': '21.7 立方码',
    // --- Gallery viewer ---
    'zoom': '放大',
    // --- News / blog titles ---
    'What is Happening to Used Heavy Equipment Pricing?': '二手重型设备价格走势如何？',
    'Caring for Your Heavy Equipment over the Winter': '冬季重型设备养护指南',
    'Top 5 Things to Do Before Buying Heavy Equipment': '购买重型设备前的 5 项准备',
    'How to Buy Heavy Equipment Safely & Avoid Unethical Sellers':
      '如何安全采购重型设备并规避不良商家',
    'How Often Should You Service Heavy Equipment?': '重型设备应多久保养一次？',
    'Advantages of Buying Used Construction Equipment': '购买二手工程机械的优势',
    'Eight Reasons to Finance Equipment for Your Business': '企业设备融资的八大理由',
    'Your #1 Guide to Replacing Heavy Equipment Parts': '重型设备配件更换指南',
    'What You Should Know About Your Equipment': '关于设备您应该了解的',
    // --- Equipment categories (also covered by data-zh; kept here as fallback) ---
    'Dump Truck': '自卸车', 'Tractor Truck': '牵引车', 'Concrete Mixer Truck': '混凝土搅拌车',
    'Lowbed Semi-Trailer': '低平板半挂车', 'Bulldozer': '推土机', 'Excavator': '挖掘机',
    'Boom Pump Truck': '泵车', 'Bulk Cement Semi-Trailer': '粉粒物料运输半挂车',
    'Car Carrier Semi-Trailer': '车辆运输半挂车', 'Container Semi-Trailer': '骨架式半挂车',
    'Curtain-side Semi-Trailer': '侧帘半挂车', 'Dump Semi-Trailer': '自卸半挂车',
    'Forklift': '叉车', 'Truck Crane': '汽车起重机', 'Backhoe Loader': '挖掘装载机',
    'Fence Semi-Trailer': '仓栅式半挂车', 'Flatbed Semi-Trailer': '平板半挂车',
    'Fuel Tanker Truck': '油罐车', 'Road Roller': '压路机', 'Truck-Mounted Crane': '随车吊',
    'Water Tank Truck': '洒水车',
    // --- Home intro, news titles, testimonials ---
    'We provide heavy-duty equipment for a variety of industries. companies all over the world buy & rent our equipment to make their work safe, reliable, and efficient.': '我们为各类行业提供重型设备。全球各地的公司采购和租赁我们的设备，让作业更安全、可靠、高效。',
    'Construction Equipment Maintenance During Winter': '冬季工程机械养护',
    'How to Buy Heavy Equipment & Avoid Unethical Sellers': '如何采购重型设备并规避不良商家',
    'Top 5 Things to Do Before Buying Construction Equipment': '购买工程机械前的 5 项准备',
    'One of the biggest factors in my buying decisions is dealer support. EquipSupply has provided us great service after the sale, so we’ve continued to work with them from sales, rental and service standpoints.': '影响我采购决策的最大因素之一是经销商的售后支持。EquipSupply 在售后给了我们极好的服务，因此我们持续在销售、租赁和服务各方面与他们合作。',
    'EquipSupply is our preferred supplier for our heavy machinery rental and purchase requirements. They have been working with us for more than 3 years now and have maintained a very professional business relationship.': 'EquipSupply 是我们重型机械租赁和采购的首选供应商。他们与我们合作超过 3 年，始终保持非常专业的业务关系。',
    'We recently used EquipSupply for the rent of a 20 tonne crawler excavator. The equipment was in good condition and was supplied with the correct attachments for the job as agreed. Thank you!': '我们最近向 EquipSupply 租赁了一台 20 吨履带式挖掘机。设备状况良好，并按约定配备了作业所需的合适属具。谢谢！',
    'From service to sales and office personnel, EquipSupply keeps our materials and products moving in an efficient and professional manner. Our yearly PM agreement ensures safe operation of our various fork trucks, manual lifts, and aerial lift.': '从服务、销售到办公室人员，EquipSupply 都以高效专业的方式保障我们的物料和产品运转。我们的年度保养协议确保了各类叉车、手动搬运车和高空作业平台的安全运行。'
  };

  var els = []; // {el, en}

  function isLangControl(el) {
    return el && (el.id === 'lang-floating' ||
      (el.classList && el.classList.contains('lang-btn')));
  }

  function collect() {
    var nodes = document.querySelectorAll('body *');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (isLangControl(el)) continue;
      if (el.children.length > 0) continue; // only leaf nodes
      var txt = (el.textContent || '').trim();
      if (!txt) continue;
      els.push({ el: el, en: txt });
    }
  }

  function zhOf(o) {
    if (o.el.dataset && o.el.dataset.zh) return o.el.dataset.zh;
    if (DICT[o.en]) return DICT[o.en];
    var m = o.en.match(/^(\d+)\s+models$/);
    if (m) return m[1] + ' 款设备';
    return null;
  }

  function applyLang(lang) {
    document.documentElement.lang = (lang === 'zh') ? 'zh-CN' : 'en';
    els.forEach(function (o) {
      if (lang === 'zh') {
        var zh = zhOf(o);
        if (zh !== null) o.el.textContent = zh;
      } else {
        o.el.textContent = o.en;
      }
    });
    updateBtn(lang);
  }

  function buildUI() {
    var box = document.createElement('div');
    box.id = 'lang-floating';
    var a1 = document.createElement('a');
    a1.className = 'lang-btn'; a1.textContent = '中文'; a1.href = '#'; a1.dataset.lang = 'zh';
    var sep = document.createElement('span');
    sep.className = 'lang-sep'; sep.textContent = '|';
    var a2 = document.createElement('a');
    a2.className = 'lang-btn'; a2.textContent = 'EN'; a2.href = '#'; a2.dataset.lang = 'en';
    box.appendChild(a1); box.appendChild(sep); box.appendChild(a2);
    box.addEventListener('click', function (e) {
      var t = e.target;
      if (t && t.classList && t.classList.contains('lang-btn')) {
        e.preventDefault();
        setLang(t.dataset.lang);
      }
    });
    document.body.appendChild(box);

    var st = document.createElement('style');
    st.textContent =
      '#lang-floating{position:fixed;top:12px;right:12px;z-index:99999;' +
      'background:rgba(33,33,33,.86);border-radius:6px;padding:5px 11px;' +
      'font:13px/1.4 Arial,Helvetica,sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.3)}' +
      '#lang-floating a{color:#fff;text-decoration:none;padding:0 5px;opacity:.55;font-weight:400}' +
      '#lang-floating a.active{opacity:1;font-weight:700;color:#ffd54f}' +
      '#lang-floating .lang-sep{color:#fff;opacity:.35}' +
      '@media (max-width:767px){#lang-floating{top:8px;right:8px;padding:4px 9px;font-size:12px}}';
    document.head.appendChild(st);
  }

  function updateBtn(lang) {
    var box = document.getElementById('lang-floating');
    if (!box) return;
    var btns = box.querySelectorAll('.lang-btn');
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.toggle('active', btns[i].dataset.lang === lang);
    }
  }

  function setLang(lang) {
    try { localStorage.setItem('site_lang', lang); } catch (e) {}
    applyLang(lang);
  }

  function init() {
    buildUI();
    collect();
    var params = new URLSearchParams(location.search);
    var lang = params.get('lang');
    if (!lang) {
      try { lang = localStorage.getItem('site_lang') || 'en'; } catch (e) { lang = 'en'; }
    }
    applyLang(lang);
  }

  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
