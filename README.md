<!--
 * @Author: Maonan Wang
 * @Date: 2025-01-13 19:24:39
 * @LastEditTime: 2025-07-10 20:50:04
 * @LastEditors: WANG Maonan
 * @Description: VLM for TSC
 * @FilePath: /VLM-TSC/README.md
-->
# 不同交通场景

存在由于突发情况导致道路无法通行的情况，如下图所示：

<div align=center>
   <img src="./assets/safety_barriers_example.png" width="30%" >
</div>


下图展示了 `RL` 的方法在遇到突发情况导致的无法通行时，不能很好处理，仍然将绿灯给不能通行的方向：

<div align=center>
   <img src="./assets/rl_for_safety_barriers.gif" width="85%" >
</div>