select sum(a.value * b.value) as result
from a left join b on a.col_num=b.row_num
where a.row_num=2 and b.col_num=3
group by a.row_num, b.col_num;


-- matrix multiply!
--select a.row_num, b.col_num, sum(a.value * b.value) as result
--from a left join b on a.col_num=b.row_num
--group by a.row_num, b.col_num;