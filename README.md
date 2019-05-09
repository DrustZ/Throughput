# Text Entry Throughput

The code accompanying our [paper](http://doi.acm.org/10.1145/3290605.3300866) for calculating text entry Throughput

Here's my [blog on throughput](https://drustz.com/posts/2019/04/28/Throughput1/) explaining all the magic

The text test platform is also available [here](https://github.com/DrustZ/TextTestPP).

## Getting Started

If you want to use this code to calculate the throughput for your transcription experiments, please first download all the codes. The ensure that your experiment data is stored in a json file. The json file includes information Present string, Transcribed string and total time. 

For each json file, the code will output one throughput. Thus you may want to create one json file for one participant under one test condition.

For guidance on how to create json file and run the code, please refer to the example.json and Example.py.

### Prerequisites

numpy

## Code Author

* [**Mingrui "Ray" Zhang**](http://drustz.com)

## Citation
If you use the code in your paper, then please cite it as:

```
@inproceedings{mingrui2019tp,
  author    = {Mingrui “Ray” Zhang, Shumin Zhai, Jacob O. Wobbrock.},
  title     = "{Text Entry Throughput: Towards Unifying Speed and Accuracy in a Single Performance Metric.}",
  booktitle = {Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems},
  year      = 2019,
  url 		= {http://doi.acm.org/10.1145/3290605.3300866},
  doi 		= {10.1145/3290605.3300866},
  publisher = {ACM},
  address 	= {New York, NY, USA},
}
```

## Acknowledgments

* We thank Kyle Gorman for her [gist](https://gist.github.com/kylebgorman/8034009) of calculating Editting distance
