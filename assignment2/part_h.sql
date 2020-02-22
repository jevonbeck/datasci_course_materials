select sum(f1.count * f2.count)
from Frequency f1 left join Frequency f2 on f1.term=f2.term and f1.docid < f2.docid
where f1.docid = '10080_txt_crude' and f2.docid = '17035_txt_earn'
group by f1.docid, f2.docid;


-- Generic similarity matrix calculation S=DD^T
--select a.row_num, b.row_num, sum(a.value * b.value)
--from a left join b on a.col_num=b.col_num and a.row_num < b.row_num
--group by a.row_num, b.row_num;