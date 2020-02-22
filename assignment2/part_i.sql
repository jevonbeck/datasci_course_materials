CREATE VIEW temp AS
SELECT * FROM frequency where term in ('washington', 'taxes', 'treasury')
UNION
SELECT 'q' as docid, 'washington' as term, 1 as count
UNION
SELECT 'q' as docid, 'taxes' as term, 1 as count
UNION
SELECT 'q' as docid, 'treasury' as term, 1 as count;

CREATE VIEW res_temp AS
select f2.docid as docid, sum(f1.count * f2.count) as similarity
from temp f1 left join temp f2 on f1.term=f2.term and f1.docid > f2.docid
where f1.docid = 'q'
group by f1.docid, f2.docid;

select max(similarity) from res_temp;

DROP VIEW res_temp;
DROP VIEW temp;