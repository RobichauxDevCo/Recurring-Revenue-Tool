# Recurring-Revenue-Tool
This tool is a comprehensive solution for managing and analyzing recurring revenue data. It allows users to import deal data, input recurring revenue details, and project revenue streams over time. Key features include:

CSV File Import:

Supports importing deal data with necessary fields like Deal Stage, Deal Name, Close Date, and Amount.
Filters deals to focus on those in qualified stages such as Proposal/Contract, Qualified Lead, and Closed won.
Recurring Revenue Details:

Input and save details such as recurring revenue amount, projected close percentage, inactive date, and reason for inactivity.
Automatically adjusts forecasted revenue based on the projected close percentage.
Ensures each deal has a single active recurring revenue entry. Existing data for the same deal is replaced on update.
Revenue and Loss Analysis:

Generates monthly recurring revenue projections starting from the deal's close date and ending on the inactive date.
Visualizes revenue and losses in a grouped bar chart, clearly distinguishing gains and losses for each month.
Dynamic Revenue Summary:

Displays a summary table of total recurring revenue and losses by month.
Includes a separate table for saved recurring revenue details, showing all active deal entries.
Edit and Delete Functionality:

Allows users to delete specific recurring revenue entries by selecting the relevant row.
Includes a feature to remove revenue data for deals marked as Closed lost or Closed stalled.
State Management:

Uses session state to maintain data persistently across interactions.
Automatically updates calculations and charts when data is added, modified, or deleted.
This tool is ideal for businesses seeking to forecast revenue, monitor recurring streams, and understand financial impacts due to changes in deal activity.
