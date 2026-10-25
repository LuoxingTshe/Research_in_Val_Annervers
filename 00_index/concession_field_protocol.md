# Concession 字段协议

本项目任何表格或图层（GeoJSON、CSV、SQLite 视图）要记录“某地物与水力特许权的关系”时，都使用本协议的字段名和取值。首次使用者：`02_outputs/concession_objects_merged/`（由 `04_pipeline/scripts/build_merged_objects.py` 生成并校验）。

## 1. 概念

| 角色 | 含义 | 本项目例子 |
|---|---|---|
| 授予方（concédant） | 拥有水力支配权并授出特许权的公共主体。Valais 为市镇（Rhône、Léman 归州）；Vaud、Fribourg 为州 | 上段：`municipal + kantonal` |
| 特许权人（concessionnaire） | 在期限内取得水力使用权的主体，期限内也是特许权设施的所有人 | FMG |
| 股东 | 持有特许权人公司股本的主体，不是特许权人 | Alpiq 持有 FMG 股份 |
| 运营方 | 受托运行设施，不是特许权人 | Hydro Exploitation |
| 受益方 | 特许权条款为其保留水量，本身不持有特许权 | Niouc、Briey 灌溉团体 |

一个主体可以同时有几种身份（例如 Anniviers 既是授予方又是 FMG 股东），但每个字段只记录一种身份。物权意义上的所有人另记在 `Owner`，不在本协议字段内。

## 2. 字段

| 字段 | 类型 | 内容 |
|---|---|---|
| `Concession_Relation` | 文本，受控 | 地物与特许权的关系，取值见第 3 节；多项用“；”连接 |
| `Concession_Scope` | 文本 | 特许权组名称，如 `上段Gougra`、`下段Navizence`、`Haute-Printse`、`Grande Dixence`、`Hongrin-Léman` |
| `Concession_Grantor` | 文本，受控 | 授予方，只能取 `municipal`、`kantonal`、`municipal + kantonal`（见第 4 节第 8 条） |
| `Concession_Holder` | 文本 | 现特许权人 |
| `Concession_Term` | 文本 | 期限 `起–止`（年）；未知端写 `?`，如 `?–2031` |
| `Concession_End` | 整数 | 所列特许权中最早的届满年，便于按年份着色或筛选 |
| `Concession_Note` | 文本 | 授予方的具体名称（以 `授予方：` 开头）、授予日期与起算日之差、历史转让、保留水量、回归安排、协议对方等 |
| `Concession_Source` | 文本 | 证据：rights_dataset 关系 ID、timeline 记录号 `R…`、文献页码或网页 |

`Concession_1…n` 与 `Concession_n_Event` 是另一类字段：它们按年份逐条记录事件（授予、转让、届满、协议等），不属于本协议。

## 3. `Concession_Relation` 取值

| 取值 | 何时使用 | Scope／Grantor／Holder／Term／End |
|---|---|---|
| `特许权` | 地物是特许权标的（水体）或特许权资产（坝、电站、引水） | 必填 |
| `特许权条款受益` | 特许权文书为该地物保留水量，但它不持有特许权 | 填所涉特许权的值 |
| `供水协议` | 与特许权人另签供水、和解、付费协议 | `不适用`；End 为空 |
| `土地使用协议` | 租赁、转租、免费使用土地 | `不适用`；End 为空 |
| `无` | 与任何特许权无关 | `不适用`；End 为空 |

## 4. 规则

1. 空值和 `不适用` 含义不同：空值表示未知，`不适用` 表示该关系下这个字段没有意义。未知也不能写成 0。
2. 一个地物涉及多项特许权时，Scope、Grantor、Holder、Term 用 ` | `（空格竖线空格）按同一顺序对齐。例如 Navizence：`上段Gougra | 下段Navizence`。
3. 授予方的层级按全部共同授予成员确定，不能只看水体所在市镇。例如上段有 Valais 州参与，应写 `municipal + kantonal`。全部成员名称写进 Note；组名不能当作法人。
4. Holder 写现特许权人。历史持有人（1943 年私人、Isotherme 等）写在 Note 中，或记为 `Concession_n` 事件。
5. 供水协议不等于特许权转让，股东不等于特许权人，届满（future）不等于已经回归。
6. Term 以期限起算年为准。授予年与起算年不同时，在 Note 中写明，例如 Hongrin：1963 年授予，1971 年起算。
7. 每行都必须填 Source。
8. 公共主体只写层级，不写名称。市镇（commune／Gemeinde，含历史市镇）写 `municipal`，州（canton／Kanton）写 `kantonal`，市镇与州共同授予写 `municipal + kantonal`。具体名称写进对应的 Note（`Concession_Note` 以 `授予方：` 开头，`Owner_Note` 写在开头）。本条适用于 `Concession_Grantor`，也适用于与本协议同表使用的 `Owner`。
   - `Owner` 只在所有权不完整或不确定时，才可在后面加全角括号限定，如 `municipal（管理）`（仅知由市镇管理）、`municipal（取水权）`。
   - 公司、灌溉团体、协会等非公共主体照写名称。
   - 多项特许权仍按第 2 条用 ` | ` 对齐，如 `municipal + kantonal | municipal`。

## 5. 校验

`build_merged_objects.py` 中的 `check_concession()` 和 `check_owner()` 负责校验：Relation 只能取受控值；Grantor 各段只能取第 8 条的三个值；Owner 不得出现公共主体名称；有特许权的行 Scope、Grantor、Holder、Term 都必填，End 必须是整数，且 ` | ` 的个数一致；其余各行这些字段必须为 `不适用`，End 为空。在其他地方复用本协议时，应照搬这段校验。
