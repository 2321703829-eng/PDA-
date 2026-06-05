Feature: ERP单据查询中心
  作为数据看板 BI 使用者
  我需要实时查询每天产生的 ERP 业务单据
  以便从一个入口查看订单、出入库、退货、补货和库存移动数据

  Background:
    Given 系统已安装模块 "logistics_web" 和 "erp_base"
    And 当前用户拥有 "物流分析查看" 权限
    And 数据看板 BI 下存在菜单 "ERP单据查询"
    And ERP单据查询接口为 "/api/admin/logistics/erp-documents/search"

  Scenario: 默认进入页面时查询最近单据
    Given 系统中存在最近 30 天内的采购订单、销售订单和出入库单
    When 用户打开 "ERP单据查询" 页面
    Then 页面默认选择 "全部单据"
    And 默认日期范围为最近 30 天
    And 列表按最近更新时间从新到旧展示
    And 每页默认显示 20 条记录

  Scenario: 实时查询新产生的销售退货单
    Given 已存在客户 "永辉超市"
    And 已创建销售退货单 "RT-001"
    When 用户在 ERP单据查询页面点击 "查询"
    Then 列表中可以看到单据 "RT-001"
    And 单据类型显示为 "销售退货单"
    And 单据状态与 Odoo 原始退货单状态一致

  Scenario: 按单据类型筛选销售退货入库单
    Given 系统中存在销售退货入库单 "IN-RT-001"
    And 系统中存在销售订单 "SO-001"
    When 用户选择单据类型 "销售退货入库单"
    And 点击 "查询"
    Then 列表只展示销售退货入库相关单据
    And 列表中包含 "IN-RT-001"
    And 列表中不展示 "SO-001"

  Scenario: 使用关键字查询供应商或客户相关单据
    Given 系统中存在供应商 "鲜食供应商A"
    And 供应商 "鲜食供应商A" 关联采购订单 "PO-001"
    When 用户在关键字输入框中输入 "鲜食供应商A"
    And 点击 "查询"
    Then 列表中展示采购订单 "PO-001"
    And 往来对象显示为 "鲜食供应商A"

  Scenario: 分页查询保持从新到旧顺序
    Given 当前筛选条件下存在超过 20 条 ERP 单据
    When 用户打开 "ERP单据查询" 页面
    Then 页面显示第一页记录
    And 第一页记录按最近更新时间从新到旧排列
    When 用户点击 "下一页"
    Then 页面显示第二页记录
    And 第二页最早记录不应晚于第一页最后一条记录

  Scenario: 点击查看进入原始业务单据
    Given 列表中存在销售订单 "SO-001"
    When 用户点击 "SO-001" 所在行的 "查看"
    Then 系统打开 Odoo 原始销售订单表单
    And 原有销售订单流程不被 ERP单据查询页面修改

  Scenario: 无数据时展示空状态
    Given 当前筛选条件下没有 ERP 单据
    When 用户点击 "查询"
    Then 页面显示 "当前条件下暂无单据数据"
    And 页面不报错

  Scenario: 无权限用户不能查看查询中心
    Given 当前用户没有 "物流分析查看" 权限
    When 用户请求 ERP单据查询接口
    Then 系统返回无权限提示
    And 不返回任何 ERP 单据明细
