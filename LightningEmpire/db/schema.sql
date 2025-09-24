CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    platform TEXT,         -- Uber / Foodpanda
    status TEXT,           -- pending / dispatched / completed
    amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    net_amount DECIMAL(10,2),
    fee DECIMAL(10,2),
    settled_at TIMESTAMP
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    action TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
