---
layout: post
title: "mapreduce源码分析-1"
tags:
  - hadoop
closeToc: true
---

自定义一个 wordcount 的 job，并藉此深入源码。

<!-- more -->

# 1. job 示例

**MyWordCount**

```java
package wordcount;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

/**
 * @author liyu
 */
public class MyWordCount {
    public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {
        Configuration conf = new Configuration();
        Job job = Job.getInstance();

        job.setJarByClass(MyWordCount.class);

        job.setJobName("MyWordCount");

        // hdfs目录
        Path inPath = new Path("/user/root/test.txt");
        Path outPath = new Path("/output/wordcount");

        FileInputFormat.addInputPath(job,inPath);

        // 如果输出路径存在，就删除
        if(outPath.getFileSystem(conf).exists(outPath)){
            outPath.getFileSystem(conf).delete(outPath,true);
        }

        // 设置输出
        FileOutputFormat.setOutputPath(job,outPath);
        // 手动创建 MyMapper.class,MyReducer.class
        job.setMapperClass(MyMapper.class);
        // 告知reduce，map输出的数据类型，否则reduce无法反序列化，会报错
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(IntWritable.class);
        job.setReducerClass(MyReducer.class);

        // Submit the job, then poll for progress until the job is complete
        job.waitForCompletion(true);
    }
}
```

**MyMapper**

```java
package wordcount;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;
import java.util.StringTokenizer;

/**
 * @author liyu
 * Mapper泛型  keyIn valueIN keyOut valueOut，输入输出都是k-v类型
 * 默认keyIn:一行首字符的下标索引 valueIn:一行的内容
 * 注意：不支持基本类型，String类型用Text代替，int用IntWritable代替
 */
public class MyMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    // 每次计数为1
    private Text word = new Text();

    @Override
    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        // 每行执行一次map方法
        StringTokenizer itr = new StringTokenizer(value.toString());
        // 将字符串放到迭代器中
        // 通过迭代器对字符串进行切割
        while (itr.hasMoreTokens()) {
            // itr.nextToken() 返回String，此处将String封装到Text中
            word.set(itr.nextToken());
            context.write(word, one);
            // 将单词装到context中，每次计数为1
            // word 对应keyOut,one对应 valueOut
            // 最后输出形式：
            // hello 1
            // hadoop 1
            // hello 1
            // hello 1
            // ...
        }
    }
}
```

**MyReducer**

```java
package wordcount;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.util.bloom.Key;

import java.io.IOException;
import java.util.Iterator;

/**
 * @author liyu
 * keyIn:从map端来，为Text
 * ValueIn:word计数，为IntWritable
 * keyOut:输出到文件的类型，单词本身，Text
 * valueOut:输出到文件的类型，单词的出现次数，IntWritable
 */
public class MyReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private IntWritable result = new IntWritable();

    // 这里是 key 和 values ，也就是一个key下多个value。和reduce同一个key为一组，计算一次相符合。
    // 每个key执行一遍该方法，进行一次迭代
    @Override
    public void reduce(Text key, Iterable<IntWritable> values,
                       Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            // 这里的val都为1，进行累加运算
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
    }
}

```

# 2. 源码解析
