register s3n://uw-cse-344-oregon.aws.amazon.com/myudfs.jar

-- load the test file into Pig
raw = LOAD 's3n://uw-cse-344-oregon.aws.amazon.com/cse344-test-file' USING TextLoader as (line:chararray);

-- parse each line into ntriples
ntriples = foreach raw generate FLATTEN(myudfs.RDFSplit3(line)) as (subject:chararray,predicate:chararray,object:chararray);

--group the n-triples by subject column
subjects1 = FILTER ntriples BY subject matches '.*business.*';

--group the n-triples by subject column
subjects2 = FILTER ntriples BY subject matches '.*business.*';

sub_obj = JOIN subjects1 BY subject, subjects2 BY subject;

dist_sub_obj = DISTINCT sub_obj;


grouped_res = group dist_sub_obj All;
res = foreach grouped_res generate COUNT(dist_sub_obj);

-- store the results in the folder /user/hadoop/example-results
fs -rm -r /user/hadoop/question3a
store res into '/user/hadoop/question3a' using PigStorage();
fs -getmerge /user/hadoop/question3a question3a.txt

-- Alternatively, you can store the results in S3, see instructions:
-- store count_by_object_ordered into 's3n://superman/example-results';
