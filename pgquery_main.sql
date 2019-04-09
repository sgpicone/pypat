select 
	case when (c.service_id = '4') then 'Friday'
	when (c.service_id = '3') then 'Thursday'
	when (c.service_id = '2') then 'Mon-Wed'
	when (c.service_id = '1') then 'Sat-Sun'
	end as DAY,
	s.stop_id, 
	s.stop_name, 
	st.departure_time,
	st2.arrival_time,
	CASE WHEN (date(c.start_date) < date(now()) and 
		   date(c.end_date) > date(now())) 
	     THEN 'VALID'
	ELSE
	     'INVALID' 
	END as CURRENT
from stop_times st
	join stop_times st2 on st.trip_id = st2.trip_id
    join stops s on s.stop_id = st.stop_id
    join trips t on t.trip_id = st.trip_id
    join calendar c on c.service_id = t.service_id
where t.service_id = '4' and 
    st2.stop_id = '240' and
    t.trip_headsign LIKE 'LINDENWOLD%' and
    st.arrival_time > '15:30:00' and st.arrival_time < '16:30:00' and
    st.stop_id = '248';
