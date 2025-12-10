
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt

billing_path = "/Volumes/workspace/default/finops_project/billing.csv.csv"
util_path = "/Volumes/workspace/default/finops_project/utilization.csv.csv"
instance_path = "/Volumes/workspace/default/finops_project/instance_mapping.csv.csv"

billing_df = pd.read_csv(billing_path)
util_df = pd.read_csv(util_path)
instance_df = pd.read_csv(instance_path)

billing_df.head(), util_df.head(), instance_df.head()
billing_df['date'] = pd.to_datetime(billing_df['date'], format='%d-%m-%Y')
billing_df['cost'] = billing_df['cost'].astype(float)
billing_df['service'] = billing_df['service'].astype(str)
daily_cost = billing_df.groupby('date')['cost'].sum().reset_index()
daily_cost.rename(columns={'cost': 'total_cost'}, inplace=True)
daily_cost.head()
service_cost = billing_df.groupby(['date','service'])['cost'].sum().reset_index()
service_cost.head()
Q1 = daily_cost['total_cost'].quantile(0.25)
Q3 = daily_cost['total_cost'].quantile(0.75)
IQR = Q3 - Q1

threshold = Q3 + 1.5 * IQR

spikes = daily_cost[daily_cost['total_cost'] > threshold]
spikes
df = daily_cost.rename(columns={'date':'ds', 'total_cost':'y'})

model = Prophet()
model.fit(df)

future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)
fig = model.plot(forecast)
plt.title("Cloud Cost Forecast")
plt.show()
idle_resources = util_df[
    (util_df['cpu_usage'] < 10) |
    (util_df['memory_usage'] < 20) |
    (util_df['hours_idle'] > 24) |
    (util_df['owner_tag'].isna()) |
    (util_df['env_tag'].isna())
]

idle_resources
merged = util_df.merge(instance_df, on='resource_id', how='left')
recommendations = []

for _, row in merged.iterrows():
    rec = ""

    if row['cpu_usage'] < 20:
        rec += "Downsize instance; "

    if row['memory_usage'] < 30:
        rec += "Memory under-utilized; "

    if row['hours_idle'] > 24:
        rec += "Schedule shutdown / quarantine; "

    if rec == "":
        rec = "Instance optimized"

    recommendations.append(rec)

merged['recommendation'] = recommendations
merged[['resource_id','instance_type','cpu_usage','memory_usage','recommendation']]
def explain_spike(cost, avg):
    if cost > avg * 2:
        return "Cost spiked due to heavy autoscaling or sudden traffic surge."
    elif cost > avg * 1.5:
        return "Possible workload increase or provisioning of new resources."
    else:
        return "Minor drift detected."
    
avg_cost = daily_cost['total_cost'].mean()

spikes['reason'] = spikes['total_cost'].apply(lambda x: explain_spike(x, avg_cost))
spikes
daily_cost.to_csv("daily_cost_output.csv", index=False)
spikes.to_csv("spikes_output.csv", index=False)
idle_resources.to_csv("idle_resources_output.csv", index=False)
merged.to_csv("optimization_output.csv", index=False)

