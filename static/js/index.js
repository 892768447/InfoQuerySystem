layui.use(['jquery', 'element'], function() {
  var $ = layui.jquery,
    element = layui.element;

  /**
   * 重新计算iframe高度
   */
  function resizeFrame() {
    var h = $(window).height() - 100;
    $("iframe").css("height", h + "px");
  }
  $(window).resize(function() {
    resizeFrame();
  });

  /**
   * 增加、删除、切换标签
   */
  var tab = {
    tabAdd: function(title, url, index) {
      //判断当前index的元素是否存在于tab中
      if($(".layui-tab-card li[lay-id=" + index + "]").length > 0) {
        //切换到该tab
        element.tabChange('nav_tab', index);
        return;
      }
      element.tabAdd('nav_tab', {
        title: title,
        id: index,
        content: '<iframe data-id="' + index + '" class="bodyFrame" frameborder="0" scrolling="yes" src="' + url + '"></iframe>'
      });
      element.tabChange('nav_tab', index);
      resizeFrame();
    },
    tabDel: function(index) {
      //删除指定Tab
      element.tabDelete('nav_tab', index);
    },
    tabChange: function(index) {
      //切换到指定Tab项
      element.tabChange('nav_tab', index);
    },
    tabDelAll: function() {}
  };

  /**
   * 左侧菜单点击事件
   * 如果没有打开页面则新增并打开
   */
  $('.layui-nav-tree li a').click(function(event) {
    var url = $(this).data('href');
    var title = $(this).text();
    var index = $('.layui-nav-tree li a').index($(this));
    //遍历iframe
    for(var i = 0; i < $('.bodyFrame').length; i++) {
      if($('.bodyFrame').eq(i).data('id') === index) {
        tab.tabChange(index);
        event.stopPropagation();
        return;
      }
    }
    tab.tabAdd(title, url, index);
  });
});