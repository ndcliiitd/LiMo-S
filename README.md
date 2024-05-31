# LiMo-S:  – An intelligent library model for sequential Cell
Developing a robust timing verification and signoff framework using machine learning 

Pooja Beniwal, PhD Scholar, IIIT-Delhi, Email: poojabe@iiitd.ac.in, Linkedin Profile:https://www.linkedin.com/in/poojabeniwal/ 

Guide: Dr. Sneh Saurabh, Associate Professor, IIIT-Delhi, Email: sneh@iiitd.ac.in

Traditional methods struggle with representing complex relationships involving more than three factors, which is increasingly problematic as modern semiconductor designs grow more intricate. In particular, the conventional flip-flop models in libraries tend to be overly pessimistic. Static timing analysis (STA), used to ensure the temporal safety of synchronous designs, relies on timing attributes of flip-flops and other cells fetched from technology libraries, typically formatted in Synopsys Liberty. Traditionally, flip-flop timing is modeled by setup time (ST), hold time (HT), and clock-to-Q (C2Q) delays, with SPICE simulations performed for each flip-flop to store relevant timing information. These attributes are modeled as separate two-dimensional lookup tables (LUTs), using conservative values to prioritize design safety. Consequently, traditional STA using these library models tends to be pessimistic.

To address these challenges and enhance the accuracy of timing models in VLSI design, our problem statement is defined as follows:

Create Timing Models of Flip-flops Using Machine Learning: Our primary objective is to develop timing models utilizing Machine Learning (ML) techniques that can account for and represent complex relationships involving more than three factors. These models will incorporate variables such as process (P), voltage (V), temperature (T), data slew (d_slew), clock slew (clk_slew), setup skew (setup_skew), hold skew (hold_skew), and the load at the Q-pin to predict the C2Q delay for flip-flops.

Establish a User-Friendly Framework: We aim to create a user-friendly framework for developing ML-based flip-flop timing models, making it easier to implement and integrate these advanced models into the VLSI design process.

LiMo-S is a user-friendly intelligent library model framework designed to overcome the limitations of traditional lookup table library-based methods. This framework automates the creation of Machine Learning (ML)-based timing models.  The main purpose of LiMo-S is to simplify the generation of datasets essential for training models. By automating this process, LiMo-S eliminates the need for manual data creation, saving users time and effort. The interface offers various commands, each designed to automate specific aspects of the modeling process. For instance, 'genDataset' initiates dataset generation using multiprocessing and optimization methods tailored for specific cell. Commands like 
'viewDataset' and 'loadData' make it easy to view and load generated datasets, while 'plotData' and 'infoData' provide visualizations and information for better comprehension.The 'splitData' command allows users to segment datasets for training and testing, contributing to robust model development. Additionally, LiMo-S's 'trainModel' and 'testModel' commands offer a seamless process for training and testing machine learning models and assessing their performance, providing insightful reports. Overall, LiMo-S streamlines the entire process of creating, visualizing, training and testing ML-based timing models, making it a valuable tool in timing verification.
