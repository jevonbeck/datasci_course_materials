select count(f.docid) from Frequency f
join (select docid from Frequency where term ='world') temp on f.docid=temp.docid
where f.term ='transactions';