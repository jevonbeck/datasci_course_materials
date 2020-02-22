select count(*) from (
    select distinct docid from Frequency where term in ('law', 'legal')
);
