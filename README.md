<!--
 * @Author: Maonan Wang
 * @Date: 2025-01-13 19:24:39
 * @LastEditTime: 2025-07-14 12:43:02
 * @LastEditors: WANG Maonan
 * @Description: VLM for TSC
 * @FilePath: /VLM-TSC/README.md
-->
# 不同交通场景

由于突发情况导致道路无法通行的情况。下图展示了 `RL` 的方法在遇到突发情况导致的无法通行时，不能很好处理，仍然将绿灯给不能通行的方向：

<div align=center>
   <img src="./assets/rl_for_safety_barriers.gif" width="85%" >
</div>

下面是每个方向渲染得到的画面，可以看到由于路障的存在，导致南侧方向一段时间内无法通行：

| BEV       | North     | East      | South     | West      |
|-----------|-----------|-----------|-----------|-----------|
| ![BEV](./assets/safety_barriers/bev.gif) | ![North](./assets/safety_barriers/north.gif) | ![East](./assets/safety_barriers/east.gif) | ![South](./assets/safety_barriers/south.gif) | ![West](./assets/safety_barriers/west.gif) |