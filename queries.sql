-- Package Delivery Database | CSC4710/6710 Group 26 | planned queries
-- Edit the sample parameters marked [PARAM] to try other packages/trucks.

-- Q1a. Full tracking history of one package            [PARAM: tracking number]
SELECT p.tracking_number, te.event_time, te.event_type,
       l.location_type, COALESCE(l.name, l.street_number || ' ' || l.street_name) AS place,
       l.city, l.state_province
FROM tracking_event te
JOIN package  p ON p.package_id  = te.package_id
JOIN location l ON l.location_id = te.location_id
WHERE p.tracking_number = '9400344937265110771664'
ORDER BY te.event_time;

-- Q1b. Where was that package at a chosen past moment?   [PARAM: timestamp]
SELECT p.tracking_number, te.event_time AS last_event_time, te.event_type,
       l.location_type, COALESCE(l.name, l.street_number || ' ' || l.street_name) AS place,
       l.city, l.state_province
FROM tracking_event te
JOIN package  p ON p.package_id  = te.package_id
JOIN location l ON l.location_id = te.location_id
WHERE p.tracking_number = '9400344937265110771664'
  AND te.event_time <= TIMESTAMP '2025-12-10 12:00:00'
ORDER BY te.event_time DESC
LIMIT 1;

-- Q2a. Truck lost in an accident: who had packages on it?   [PARAM: truck]
-- "On the truck" = the package's most recent tracking event is at that truck.
SELECT p.tracking_number,
       s.name  AS sender,    s.phone AS sender_phone,
       r.name  AS recipient, r.phone AS recipient_phone,
       latest.event_type, latest.event_time
FROM location t
JOIN LATERAL (
        SELECT te.package_id, te.event_type, te.event_time
        FROM (SELECT DISTINCT package_id FROM tracking_event WHERE location_id = t.location_id) cand
        JOIN LATERAL (SELECT * FROM tracking_event e
                      WHERE e.package_id = cand.package_id
                      ORDER BY e.event_time DESC LIMIT 1) te ON TRUE
        WHERE te.location_id = t.location_id
     ) latest ON TRUE
JOIN package   p ON p.package_id   = latest.package_id
JOIN customer  s ON s.customer_id  = p.sender_id
JOIN recipient r ON r.recipient_id = p.recipient_id
WHERE t.location_type = 'TRUCK' AND t.name = 'UPS-SDF-T1'
ORDER BY latest.event_time;

-- Q2b. Last successful delivery that truck made               [PARAM: truck]
SELECT t.name AS truck, d.delivered_at, p.tracking_number,
       r.name AS recipient, d.signed_by
FROM delivery d
JOIN location  t ON t.location_id  = d.vehicle_location_id
JOIN package   p ON p.package_id   = d.package_id
JOIN recipient r ON r.recipient_id = p.recipient_id
WHERE t.name = 'UPS-SDF-T1'
ORDER BY d.delivered_at DESC
LIMIT 1;

-- Q3. Customer who shipped the most packages in the past year (ties kept)
SELECT c.customer_id, c.name, c.customer_type, COUNT(*) AS packages_shipped
FROM package p
JOIN customer c ON c.customer_id = p.sender_id
WHERE p.ship_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY c.customer_id, c.name, c.customer_type
ORDER BY packages_shipped DESC
FETCH FIRST 1 ROWS WITH TIES;

--  Customer who spent the most on shipping in the past year (ties kept)
SELECT c.customer_id, c.name, c.customer_type, SUM(p.charge) AS total_spent
FROM package p
JOIN customer c ON c.customer_id = p.sender_id
WHERE p.ship_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY c.customer_id, c.name, c.customer_type
ORDER BY total_spent DESC
FETCH FIRST 1 ROWS WITH TIES;

--  Street with the most customers (same street name + city + state)
SELECT l.street_name, l.city, l.state_province, COUNT(*) AS customers
FROM customer c
JOIN location l ON l.location_id = c.address_location_id
GROUP BY l.street_name, l.city, l.state_province
ORDER BY customers DESC
FETCH FIRST 1 ROWS WITH TIES;

--  Packages delivered later than promised
SELECT p.tracking_number, sv.service_name, d.promised_at, d.delivered_at,
       d.delivered_at - d.promised_at AS late_by
FROM delivery d
JOIN package p  ON p.package_id  = d.package_id
JOIN service sv ON sv.service_id = p.service_id
WHERE d.delivered_at > d.promised_at
ORDER BY late_by DESC;

--  Monthly bills in three forms (views, so any month can be pulled)
CREATE OR REPLACE VIEW v_bill_simple AS
SELECT c.customer_id, c.name AS customer,
       l.street_number || ' ' || l.street_name || ', ' || l.city || ', ' ||
       l.state_province || ' ' || l.postal_code AS address,
       date_trunc('month', p.ship_date)::date AS bill_month,
       SUM(p.charge) AS amount_owed
FROM package p
JOIN customer c ON c.customer_id = p.sender_id
JOIN location l ON l.location_id = c.address_location_id
GROUP BY c.customer_id, c.name, l.street_number, l.street_name, l.city,
         l.state_province, l.postal_code, date_trunc('month', p.ship_date);

CREATE OR REPLACE VIEW v_bill_by_service AS
SELECT c.customer_id, c.name AS customer,
       date_trunc('month', p.ship_date)::date AS bill_month,
       sv.service_name, COUNT(*) AS shipments, SUM(p.charge) AS subtotal
FROM package p
JOIN customer c  ON c.customer_id = p.sender_id
JOIN service  sv ON sv.service_id = p.service_id
GROUP BY c.customer_id, c.name, date_trunc('month', p.ship_date), sv.service_name;

CREATE OR REPLACE VIEW v_bill_itemized AS
SELECT c.customer_id, c.name AS customer,
       date_trunc('month', p.ship_date)::date AS bill_month,
       p.ship_date, p.tracking_number, sv.service_name, p.package_type,
       p.weight_lb, p.charge
FROM package p
JOIN customer c  ON c.customer_id = p.sender_id
JOIN service  sv ON sv.service_id = p.service_id;

-- Store one bill row per contract customer per month (safe to re-run)
INSERT INTO bill (customer_id, bill_month, total_amount)
SELECT b.customer_id, b.bill_month, b.amount_owed
FROM v_bill_simple b
JOIN customer c ON c.customer_id = b.customer_id
WHERE c.customer_type = 'CONTRACT'
ON CONFLICT (customer_id, bill_month) DO NOTHING;

-- Sample output for one customer and month        [PARAM: customer_id, month]
--  Simple bill
SELECT * FROM v_bill_simple     WHERE customer_id = 92 AND bill_month = DATE '2026-10-01';
-- . Grouped by type of service
SELECT * FROM v_bill_by_service WHERE customer_id = 92 AND bill_month = DATE '2026-10-01'
ORDER BY service_name;
--  Itemized
SELECT * FROM v_bill_itemized   WHERE customer_id = 92 AND bill_month = DATE '2026-10-01'
ORDER BY ship_date, tracking_number;

SELECT 'location' AS tbl, COUNT(*) FROM location UNION ALL
SELECT 'customer', COUNT(*) FROM customer UNION ALL
SELECT 'recipient', COUNT(*) FROM recipient UNION ALL
SELECT 'service', COUNT(*) FROM service UNION ALL
SELECT 'service_rate', COUNT(*) FROM service_rate UNION ALL
SELECT 'payment_method', COUNT(*) FROM payment_method UNION ALL
SELECT 'package', COUNT(*) FROM package UNION ALL
SELECT 'tracking_event', COUNT(*) FROM tracking_event UNION ALL
SELECT 'delivery', COUNT(*) FROM delivery UNION ALL
SELECT 'hazmat_detail', COUNT(*) FROM hazmat_detail UNION ALL
SELECT 'customs_declaration', COUNT(*) FROM customs_declaration UNION ALL
SELECT 'bill', COUNT(*) FROM bill;
