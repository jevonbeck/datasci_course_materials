select count(*) from (
    select distinct docid from Frequency
    group by docid
    having sum(count) > 300
);