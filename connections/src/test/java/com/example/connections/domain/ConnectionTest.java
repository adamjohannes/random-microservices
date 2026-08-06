package com.example.connections.domain;

import com.example.connections.domain.model.Connection;
import com.example.connections.domain.model.ConnectionStatus;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class ConnectionTest {

    @Test
    void create_setsStatusPending() {
        UUID a = UUID.randomUUID();
        UUID b = UUID.randomUUID();

        Connection c = Connection.create(a, b);

        assertThat(c.getStatus()).isEqualTo(ConnectionStatus.PENDING);
    }

    @Test
    void create_derivesIdFromSortedPair() {
        UUID a = UUID.fromString("00000000-0000-0000-0000-000000000001");
        UUID b = UUID.fromString("00000000-0000-0000-0000-000000000002");

        String id = Connection.create(a, b).getId();

        assertThat(id).isEqualTo(a + "_" + b);
    }

    @Test
    void create_idIsOrderIndependent() {
        UUID a = UUID.randomUUID();
        UUID b = UUID.randomUUID();

        String idAB = Connection.create(a, b).getId();
        String idBA = Connection.create(b, a).getId();

        assertThat(idAB).isEqualTo(idBA);
    }

    @Test
    void create_samePairProducesSameId() {
        UUID a = UUID.randomUUID();
        UUID b = UUID.randomUUID();

        String first  = Connection.create(a, b).getId();
        String second = Connection.create(a, b).getId();

        assertThat(first).isEqualTo(second);
    }
}
