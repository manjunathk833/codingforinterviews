import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * System Design Lab 03: Transactional Outbox, CDC Relay & Idempotent Consumer (Java 17).
 */
public class Solution {

    static class OutboxEvent {
        final String eventId;
        final String aggregateId;
        boolean published;

        OutboxEvent(String eventId, String aggregateId) {
            this.eventId = eventId;
            this.aggregateId = aggregateId;
            this.published = false;
        }
    }

    static class OrderStore {
        final Map<String, String> orders = new HashMap<>();
        final List<OutboxEvent> outbox = new ArrayList<>();

        void createOrderAtomic(String orderId, boolean failBeforeCommit) {
            if (failBeforeCommit) {
                throw new IllegalStateException("Simulated rollback");
            }
            orders.put(orderId, "PENDING");
            outbox.add(new OutboxEvent("evt-" + orderId, orderId));
        }
    }

    static class IdempotentConsumer {
        final Set<String> seenEvents = new HashSet<>();
        final Map<String, String> projections = new HashMap<>();
        int executions = 0;

        boolean consume(OutboxEvent evt) {
            if (!seenEvents.add(evt.eventId)) {
                return false;
            }
            projections.put(evt.aggregateId, "CONFIRMED");
            executions++;
            return true;
        }
    }

    public static void main(String[] args) {
        OrderStore store = new OrderStore();
        IdempotentConsumer consumer = new IdempotentConsumer();

        boolean rolledBack = false;
        try {
            store.createOrderAtomic("ord-fail", true);
        } catch (IllegalStateException ex) {
            rolledBack = true;
        }
        assert rolledBack : "Expected rollback exception";
        assert store.orders.isEmpty() && store.outbox.isEmpty() : "Rollback leaked state!";

        store.createOrderAtomic("ord-101", false);
        store.createOrderAtomic("ord-102", false);

        for (OutboxEvent evt : store.outbox) {
            // Deliver twice to simulate at-least-once retry
            consumer.consume(evt);
            consumer.consume(evt);
            evt.published = true;
        }

        assert consumer.executions == 2 : "Expected 2 idempotent executions, got " + consumer.executions;
        assert "CONFIRMED".equals(consumer.projections.get("ord-101"));
        assert "CONFIRMED".equals(consumer.projections.get("ord-102"));

        System.out.println("All 3 Java Transactional Outbox, CDC Relay & Idempotent Consumer test cases passed!");
    }
}
