layui.use('table', function() {
  var table = layui.table;
  return;
  table.render({
    elem: '#usertable',
    url: 'test/user.json',
    cols: [
      [{
        type: 'checkbox'
      }, {
        field: 'user_id',
        width: 80,
        title: '用户ID',
        sort: true
      }, {
        field: 'user_name',
        width: 80,
        title: '账号',
        sort: true
      }, {
        field: 'user_nick',
        width: 80,
        title: '昵称',
        sort: true
      }, {
        field: 'user_role',
        width: 80,
        title: '角色',
        sort: true
      }, {
        field: 'group_id',
        title: '分组ID',
        width: 80,
        sort: true
      }, {
        field: 'group_name',
        width: 80,
        title: '分组名',
        sort: true
      }, {
        field: 'user_state',
        width: 80,
        title: '状态',
        sort: true
      }, {
        field: 'user_ips',
        width: 80,
        title: '允许IP',
        sort: true
      }, {
        field: 'valid_time',
        width: 135,
        title: '密码到期时间',
        sort: true
      }, {
        field: 'user_mark',
        width: 135,
        title: '备注',
        sort: true
      }]
    ],
    page: true
  });
});