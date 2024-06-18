# Certificate trees generated:
#
# 1. Energy Sector Trust Framework Server CA
#     2. Energy Sector Trust Framework Server Issuer
#         3. <This computer>
#
# 4. Energy Sector Trust Framework Client CA
#     5. Energy Sector Trust Framework Client Issuer
#          6. Application One (roles: supply-voltage-reader, reporter)
#          7. Application Two (roles: consumption-reader, reporter)

# 1. Energy Sector Trust Framework Server CA
openssl genpkey -algorithm RSA -out 1-server-ca-key.pem
openssl req -new -x509 -key 1-server-ca-key.pem -out 1-server-ca-cert.pem -days 3560 -subj "/C=GB/O=Energy Sector Trust Framework/CN=Energy Sector Trust Framework Server CA"

# 2. Energy Sector Trust Framework Issuer
openssl genpkey -algorithm RSA -out 2-server-issuer-key.pem
openssl req -new -key 2-server-issuer-key.pem -out 2-server-issuer-csr.pem -subj "/C=GB/ST=London/O=Energy Sector Trust Framework/CN=Energy Sector Trust Framework Server Issuer"
openssl x509 -req -in 2-server-issuer-csr.pem -out 2-server-issuer-ca.pem -extfile ../scripts/extensions.cnf -extensions v3_ca -CA 1-server-ca-cert.pem -CAkey 1-server-ca-key.pem -days 365

# 3. <This computer>
openssl genpkey -algorithm RSA -out 3-server-key.pem
openssl req -new -key 3-server-key.pem -out 3-server-csr.pem -subj "/C=GB/ST=London/O=Energy Sector Trust Framework/CN=`hostname`"
openssl x509 -req -in 3-server-csr.pem -out 3-server-cert.pem -CA 2-server-issuer-ca.pem -CAkey 2-server-issuer-key.pem -days 365
cat 3-server-cert.pem 2-server-issuer-ca.pem > 3-server-cert-bundle.pem

# 4. Energy Sector Trust Framework Client CA
openssl genpkey -algorithm RSA -out 4-client-ca-key.pem
openssl req -new -x509 -key 4-client-ca-key.pem -out 4-client-ca-cert.pem -days 3560 -subj "/C=GB/O=Energy Sector Trust Framework/CN=Energy Sector Trust Framework Client CA"

# 5. Energy Sector Trust Framework Client Issuer
openssl genpkey -algorithm RSA -out 5-client-issuer-key.pem
openssl req -new -key 5-client-issuer-key.pem -out 5-client-issuer-csr.pem -subj "/C=GB/ST=London/O=Energy Sector Trust Framework/CN=Energy Sector Trust Framework Client Issuer"
openssl x509 -req -in 5-client-issuer-csr.pem -out 5-client-issuer-ca.pem -extfile ../scripts/extensions.cnf -extensions v3_ca -CA 4-client-ca-cert.pem -CAkey 4-client-ca-key.pem -days 365

# 6. Application One (roles: supply-voltage-reader, reporter)
openssl genpkey -algorithm RSA -out 6-application-one-key.pem
openssl req -new -key 6-application-one-key.pem -out 6-application-one-csr.pem -subj "/C=GB/ST=London/O=Application One/OU=supply-voltage-reader@electricity/OU=reporter@electricity/CN=`uuidgen`"
openssl x509 -req -in 6-application-one-csr.pem -out 6-application-one-cert.pem -CA 5-client-issuer-ca.pem -CAkey 5-client-issuer-key.pem -days 365
cat 6-application-one-cert.pem 5-client-issuer-ca.pem > 6-application-one-bundle.pem

# 7. Application Two (roles: consumption-reader, reporter)
openssl genpkey -algorithm RSA -out 7-application-two-key.pem
openssl req -new -key 7-application-two-key.pem -out 7-application-two-csr.pem -subj "/C=GB/ST=London/O=Application Two/OU=consumption-reader@electricity/OU=reporter@electricity/CN=`uuidgen`"
openssl x509 -req -in 7-application-two-csr.pem -out 7-application-two-cert.pem -CA 5-client-issuer-ca.pem -CAkey 5-client-issuer-key.pem -days 365
cat 7-application-two-cert.pem 5-client-issuer-ca.pem > 7-application-two-bundle.pem

