# gluttonous_snake
该代码为一个贪吃蛇游戏

可以实现以下功能：

1）基本的贪吃蛇游戏操作和得分计算 gluttonous_snake.py human_move.py

2）可视化得分排行榜及实现时间 update_record display_record 

3）可以对排行榜进行清除进行重新计算 clear_record

4）AI实现贪吃蛇游戏：使用广度优先搜索（BFS）和深度优先搜索（DFS）算法寻找贪吃蛇到达食物的路径的函数，以及确定蛇避开障碍物和尾随策略的安全移动函数
   
  AI_gluttonous_snake.py BFS DFS find_safe_move
  
5）利用强化学习DQN算法，并创建相应的env进行训练，并对训练结果进行可视化 train_dqn learn AI_move.py DQNnetwork.py watch_agent.py


1. Install requirements:
   Windows11
- Python == 3.7.X
- pygame == 2.5.2
- PyTorch == 1.7.1 with CUDA ==11.0 
- torchvision==0.8.2+cu110
```setup
conda env create -f environment.yml
```
2. Start
```
python gluttonous_snake.py
```
