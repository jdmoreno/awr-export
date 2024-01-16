import modules.configuration as configuration
import modules.track_elements as track_elements

accum_aggregations = {}

def aggregations():
    global accum_aggregations

    accum_aggregations.clear()

    tracker = configuration.config["TRACKER"]
    # print(f"tracker: {tracker}")
    #
    # track_sql_ids = tracker.get("track_sql_ids")
    # print(f"track_sql_ids: {track_sql_ids}")

    # Store sql ids to track
    aggregations_track_sql_ids = tracker["track_sql_ids"]

    tracked_sql_ids = track_elements.get_tracked_sql_ids()
    for sql_id in tracked_sql_ids:
        # print(f"aggregations - sql_id: {sql_id}")
        for aggregation in aggregations_track_sql_ids:
            if aggregation not in accum_aggregations.keys():
                accum_aggregations[aggregation] = 0
            # print(f"\taggregations - aggregation: {aggregation} - values: {aggregations_track_sql_ids[aggregation]} ")
            if sql_id in aggregations_track_sql_ids[aggregation]:
                # print(f"\t\tadd to aggregation: {aggregation} - sql_id: {sql_id} - executions {tracked_sql_ids[sql_id][0]}")
                accum_aggregations[aggregation] = accum_aggregations[aggregation] + tracked_sql_ids[sql_id][0]

    # print(f"aggregations: {accum_aggregations} - {accum_aggregations.keys()}")