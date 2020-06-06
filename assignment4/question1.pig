register s3n://uw-cse-344-oregon.aws.amazon.com/myudfs.jar

-- load the test file into Pig
raw = LOAD 's3n://uw-cse-344-oregon.aws.amazon.com/btc-2010-chunk-000' USING TextLoader as (line:chararray);

-- parse each line into ntriples
ntriples = foreach raw generate FLATTEN(myudfs.RDFSplit3(line)) as (subject:chararray,predicate:chararray,object:chararray);

--group the n-triples by object column
objects = group ntriples by (object) PARALLEL 50;

-- flatten the objects out (because group by produces a tuple of each object
-- in the first column, and we want each object ot be a string, not a tuple),
-- and count the number of tuples associated with each object
count_by_object = foreach objects generate flatten($0), COUNT($1) as count PARALLEL 50;

--order the resulting tuples by their count in descending order
count_by_object_ordered = order count_by_object by (count)  PARALLEL 50;

grouped_res = group count_by_object_ordered All;
res = foreach grouped_res generate COUNT(count_by_object_ordered);

-- store the results in the folder /user/hadoop/example-results
fs -rm -r /user/hadoop/question1
store res into '/user/hadoop/question1' using PigStorage();
fs -getmerge /user/hadoop/question1 question1.txt
-- Alternatively, you can store the results in S3, see instructions:
-- store count_by_object_ordered into 's3n://superman/example-results';
