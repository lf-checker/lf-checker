# Flag predictor for ESBMC Concurrency verification

This is a flag predictor developed on Machine Learning technique to give the optimal flags for ESBMC in verifying multi-threaded programs.

The public location of ESBMCs source is on github:

    https://github.com/esbmc/esbmc

```
usage: ./esbmc-wrapper.py -p propertyFile --concurrencyFlagPredictor model.sav --arch 32 benchmark
```               
### Authors
Tong Wu (University of Manchester, United Kingdom) wutonguom@gmail.com

Lucas Cordeiro (University of Manchester, United Kingdom) lucas.cordeiro@manchester.ac.uk

### Links
- [Benchexec Tool Info Module](https://github.com/sosy-lab/benchexec/blob/main/benchexec/tools/esbmc.py)
