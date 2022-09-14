from tablefaker import tablefaker

#https://faker.readthedocs.io/en/master/providers/baseprovider.html

f = tablefaker.TableFaker()
f.SetSchema('/Users/necatiarslan/GitHub/table-faker/tests/avro_schema_v1.json')
df = f.GetFakePandasDataFrame()



