class PlanningMemoryFusion:

    def fuse(self, plan, memories):

        # memory influence on planning

        enriched_plan = list(plan)

        if memories:

            # if similar past exists → prioritize memory
            enriched_plan.insert(0, "memory")

        return enriched_plan