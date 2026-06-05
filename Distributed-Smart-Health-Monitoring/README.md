Dani Feriansyah - 152024109

# Distributed Smart Health Monitoring System

## Overview

Distributed Smart Health Monitoring System is a simulation of a patient monitoring system using parallel computing concepts.

The system consists of three virtual sensors:

* Heart Rate Sensor
* Temperature Sensor
* Oxygen Saturation Sensor (SpO2)

Each sensor runs as an independent process using Python Multiprocessing and sends monitoring data simultaneously.

## Objectives

* Demonstrate parallel computing concepts.
* Simulate healthcare monitoring systems.
* Compare serial and parallel processing performance.

## Technologies

* Python 3
* Multiprocessing
* Random
* Time

## System Architecture

Heart Rate Sensor

Temperature Sensor -----> Monitoring Dashboard
/
SpO2 Sensor

## How to Run

```bash
python main.py
```

## Benchmark

```bash
python benchmark/performance_test.py
```

## Results

The sensors successfully generate and display patient health data concurrently.

Parallel execution demonstrates better performance than serial execution for large workloads.

## Team

IFB-206 Parallel Computing
