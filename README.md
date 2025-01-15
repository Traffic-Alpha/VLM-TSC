<!--
 * @Author: Maonan Wang
 * @Date: 2025-01-13 19:24:39
 * @LastEditTime: 2025-01-13 19:48:40
 * @LastEditors: Maonan Wang
 * @Description: 
 * @FilePath: /VLM-TSC/README.md
-->
- 将车辆的模型通过 release 上传，然后放在文件夹
- 构建一个稍微复杂的车流，可以出现堵车，且可以在 3D 的效果里面看到
- 使用 state rl 跑通, 然后在 image 里面收集数据
- 是否可以构造车辆撞车的图像

---

可以识别到有特殊的车辆（救护车，警车）
可以识别到撞车（SUMO 中通过设置车辆位置，让车辆进行撞车）
当出现数据丢失的时候