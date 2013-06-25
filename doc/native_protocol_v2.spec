
                             CQL BINARY PROTOCOL v2


Table of Contents

  1. Overview
  2. Frame header
    2.1. version
    2.2. flags
    2.3. stream
    2.4. opcode
    2.5. length
  3. Notations
  4. Messages
    4.1. Requests
      4.1.1. STARTUP
      4.1.2. AUTH_RESPONSE
      4.1.3. OPTIONS
      4.1.4. QUERY
      4.1.5. PREPARE
      4.1.6. EXECUTE
      4.1.7. BATCH
      4.1.8. REGISTER
      4.1.9. NEXT
    4.2. Responses
      4.2.1. ERROR
      4.2.2. READY
      4.2.3. AUTHENTICATE
      4.2.4. SUPPORTED
      4.2.5. RESULT
        4.2.5.1. Void
        4.2.5.2. Rows
        4.2.5.3. Set_keyspace
        4.2.5.4. Prepared
        4.2.5.5. Schema_change
      4.2.6. EVENT
      4.2.7. AUTH_CHALLENGE
      4.2.8. AUTH_SUCCESS
  5. Compression
  6. Collection types
  7. Result paging
  8. Error codes
  9. Changes from v1


1. Overview

  The CQL binary protocol is a frame based protocol. Frames are defined as:

      0         8        16        24        32
      +---------+---------+---------+---------+
      | version |  flags  | stream  | opcode  |
      +---------+---------+---------+---------+
      |                length                 |
      +---------+---------+---------+---------+
      |                                       |
      .            ...  body ...              .
      .                                       .
      .                                       .
      +----------------------------------------

  The protocol is big-endian (network byte order).

  Each frame contains a fixed size header (8 bytes) followed by a variable size
  body. The header is described in Section 2. The content of the body depends
  on the header opcode value (the body can in particular be empty for some
  opcode values). The list of allowed opcode is defined Section 2.3 and the
  details of each corresponding message is described Section 4.

  The protocol distinguishes 2 types of frames: requests and responses. Requests
  are those frame sent by the clients to the server, response are the ones sent
  by the server. Note however that while communication are initiated by the
  client with the server responding to request, the protocol may likely add
  server pushes in the future, so responses does not obligatory come right after
  a client request.

  Note to client implementors: clients library should always assume that the
  body of a given frame may contain more data than what is described in this
  document. It will however always be safe to ignore the remaining of the frame
  body in such cases. The reason is that this may allow to sometimes extend the
  protocol with optional features without needing to change the protocol
  version.



2. Frame header

2.1. version

  The version is a single byte that indicate both the direction of the message
  (request or response) and the version of the protocol in use. The up-most bit
  of version is used to define the direction of the message: 0 indicates a
  request, 1 indicates a responses. This can be useful for protocol analyzers to
  distinguish the nature of the packet from the direction which it is moving.
  The rest of that byte is the protocol version (2 for the protocol defined in
  this document). In other words, for this version of the protocol, version will
  have one of:
    0x02    Request frame for this protocol version
    0x82    Response frame for this protocol version

  This document describe the version 2 of the protocol. For the changes made since
  version 1, see Section 9.


2.2. flags

  Flags applying to this frame. The flags have the following meaning (described
  by the mask that allow to select them):
    0x01: Compression flag. If set, the frame body is compressed. The actual
          compression to use should have been set up beforehand through the
          Startup message (which thus cannot be compressed; Section 4.1.1).
    0x02: Tracing flag. For a request frame, this indicate the client requires
          tracing of the request. Note that not all requests support tracing.
          Currently, only QUERY, PREPARE and EXECUTE queries support tracing.
          Other requests will simply ignore the tracing flag if set. If a
          request support tracing and the tracing flag was set, the response to
          this request will have the tracing flag set and contain tracing
          information.
          If a response frame has the tracing flag set, its body contains
          a tracing ID. The tracing ID is a [uuid] and is the first thing in
          the frame body. The rest of the body will then be the usual body
          corresponding to the response opcode.

  The rest of the flags is currently unused and ignored.

2.3. stream

  A frame has a stream id (one signed byte). When sending request messages, this
  stream id must be set by the client to a positive byte (negative stream id
  are reserved for streams initiated by the server; currently all EVENT messages
  (section 4.2.6) have a streamId of -1). If a client sends a request message
  with the stream id X, it is guaranteed that the stream id of the response to
  that message will be X.

  This allow to deal with the asynchronous nature of the protocol. If a client
  sends multiple messages simultaneously (without waiting for responses), there
  is no guarantee on the order of the responses. For instance, if the client
  writes REQ_1, REQ_2, REQ_3 on the wire (in that order), the server might
  respond to REQ_3 (or REQ_2) first. Assigning different stream id to these 3
  requests allows the client to distinguish to which request an received answer
  respond to. As there can only be 128 different simultaneous stream, it is up
  to the client to reuse stream id.

  Note that clients are free to use the protocol synchronously (i.e. wait for
  the response to REQ_N before sending REQ_N+1). In that case, the stream id
  can be safely set to 0. Clients should also feel free to use only a subset of
  the 128 maximum possible stream ids if it is simpler for those
  implementation.

2.4. opcode

  An integer byte that distinguish the actual message:
    0x00    ERROR
    0x01    STARTUP
    0x02    READY
    0x03    AUTHENTICATE
    0x05    OPTIONS
    0x06    SUPPORTED
    0x07    QUERY
    0x08    RESULT
    0x09    PREPARE
    0x0A    EXECUTE
    0x0B    REGISTER
    0x0C    EVENT
    0x0D    BATCH
    0x0E    AUTH_CHALLENGE
    0x0F    AUTH_RESPONSE
    0x10    AUTH_SUCCESS
    0x11    NEXT

  Messages are described in Section 4.

  (Note that there is no 0x04 message in this version of the protocol)


2.5. length

  A 4 byte integer representing the length of the body of the frame (note:
  currently a frame is limited to 256MB in length).


3. Notations

  To describe the layout of the frame body for the messages in Section 4, we
  define the following:

    [int]          A 4 bytes integer
    [short]        A 2 bytes unsigned integer
    [string]       A [short] n, followed by n bytes representing an UTF-8
                   string.
    [long string]  An [int] n, followed by n bytes representing an UTF-8 string.
    [uuid]         A 16 bytes long uuid.
    [string list]  A [short] n, followed by n [string].
    [bytes]        A [int] n, followed by n bytes if n >= 0. If n < 0,
                   no byte should follow and the value represented is `null`.
    [short bytes]  A [short] n, followed by n bytes if n >= 0.

    [option]       A pair of <id><value> where <id> is a [short] representing
                   the option id and <value> depends on that option (and can be
                   of size 0). The supported id (and the corresponding <value>)
                   will be described when this is used.
    [option list]  A [short] n, followed by n [option].
    [inet]         An address (ip and port) to a node. It consists of one
                   [byte] n, that represents the address size, followed by n
                   [byte] representing the IP address (in practice n can only be
                   either 4 (IPv4) or 16 (IPv6)), following by one [int]
                   representing the port.
    [consistency]  A consistency level specification. This is a [short]
                   representing a consistency level with the following
                   correspondance:
                     0x0000    ANY
                     0x0001    ONE
                     0x0002    TWO
                     0x0003    THREE
                     0x0004    QUORUM
                     0x0005    ALL
                     0x0006    LOCAL_QUORUM
                     0x0007    EACH_QUORUM

    [string map]      A [short] n, followed by n pair <k><v> where <k> and <v>
                      are [string].
    [string multimap] A [short] n, followed by n pair <k><v> where <k> is a
                      [string] and <v> is a [string list].


4. Messages

4.1. Requests

  Note that outside of their normal responses (described below), all requests
  can get an ERROR message (Section 4.2.1) as response.

4.1.1. STARTUP

  Initialize the connection. The server will respond by either a READY message
  (in which case the connection is ready for queries) or an AUTHENTICATE message
  (in which case credentials will need to be provided using AUTH_RESPONSE).

  This must be the first message of the connection, except for OPTIONS that can
  be sent before to find out the options supported by the server. Once the
  connection has been initialized, a client should not send any more STARTUP
  message.

  The body is a [string map] of options. Possible options are:
    - "CQL_VERSION": the version of CQL to use. This option is mandatory and
      currenty, the only version supported is "3.0.0". Note that this is
      different from the protocol version.
    - "COMPRESSION": the compression algorithm to use for frames (See section 5).
      This is optional, if not specified no compression will be used.


4.1.2. AUTH_RESPONSE

  Answers a server authentication challenge.

  Authentication in the protocol is SASL based. The server sends authentication
  challenges (a bytes token) to which the client answer with this message. Those
  exchanges continue until the server accepts the authentication by sending a
  AUTH_SUCCESS message after a client AUTH_RESPONSE. It is however that client that
  initiate the exchange by sending an initial AUTH_RESPONSE in response to a
  server AUTHENTICATE request.

  The body of this message is a single [bytes] token. The details of what this
  token contains (and when it can be null/empty, if ever) depends on the actual
  authenticator used.

  The response to a AUTH_RESPONSE is either a follow-up AUTH_CHALLENGE message,
  an AUTH_SUCCESS message or an ERROR message.


4.1.3. OPTIONS

  Asks the server to return what STARTUP options are supported. The body of an
  OPTIONS message should be empty and the server will respond with a SUPPORTED
  message.


4.1.4. QUERY

  Performs a CQL query. The body of the message must be:
    <query><consistency><result_page_size>[<n><value_1>...<value_n>]
  where:
    - <query> the query, [long string].
    - <consistency> is the [consistency] level for the operation.
    - <result_page_size> is an [int] controlling the desired page size of the
      result (in CQL3 rows). A negative value disable paging of the result. See the
      section on paging (Section 7) for more details.
    - optional: <n> [short], the number of following values.
    - optional: <value_1>...<value_n> are [bytes] to use for bound variables in the query.

  Note that the consistency is ignored by some queries (USE, CREATE, ALTER,
  TRUNCATE, ...).

  The server will respond to a QUERY message with a RESULT message, the content
  of which depends on the query.


4.1.5. PREPARE

  Prepare a query for later execution (through EXECUTE). The body consists of
  the CQL query to prepare as a [long string].

  The server will respond with a RESULT message with a `prepared` kind (0x0004,
  see Section 4.2.5).


4.1.6. EXECUTE

  Executes a prepared query. The body of the message must be:
    <id><n><value_1>....<value_n><consistency><result_page_size>
  where:
    - <id> is the prepared query ID. It's the [short bytes] returned as a
      response to a PREPARE message.
    - <n> is a [short] indicating the number of following values.
    - <value_1>...<value_n> are the [bytes] to use for bound variables in the
      prepared query.
    - <consistency> is the [consistency] level for the operation.
    - <result_page_size> is an [int] controlling the desired page size of the
      result (in CQL3 rows). A negative value disable paging of the result. See the
      section on paging (Section 7) for more details.

  Note that the consistency is ignored by some (prepared) queries (USE, CREATE,
  ALTER, TRUNCATE, ...).

  The response from the server will be a RESULT message.

4.1.7. BATCH

  Allows executing a list of queries (prepared or not) as a batch (note that
  only DML statements are accepted in a batch). The body of the message must
  be:
    <type><n><query_1>...<query_n><consistency>
  where:
    - <type> is a [byte] indicating the type of batch to use:
        - If <type> == 0, the batch will be "logged". This is equivalent to a
          normal CQL3 batch statement.
        - If <type> == 1, the batch will be "unlogged".
        - If <type> == 2, the batch will be a "counter" batch (and non-counter
          statements will be rejected).
    - <n> is a [short] indicating the number of following queries.
    - <query_1>...<query_n> are the queries to execute. A <query_i> must be of the
      form:
        <kind><string_or_id><n><value_1>...<value_n>
      where:
       - <kind> is a [byte] indicating whether the following query is a prepared
         one or not. <kind> value must be either 0 or 1.
       - <string_or_id> depends on the value of <kind>. If <kind> == 0, it should be
         a [long string] query string (as in QUERY, the query string might contain
         bind markers). Otherwise (that is, if <kind> == 1), it should be a
         [short bytes] representing a prepared query ID.
       - <n> is a [short] indicating the number (possibly 0) of following values.
       - <value_1>...<value_n> are the [bytes] to use for bound variables.
    - <consistency> is the [consistency] level for the operation.


4.1.8. REGISTER

  Register this connection to receive some type of events. The body of the
  message is a [string list] representing the event types to register to. See
  section 4.2.6 for the list of valid event types.

  The response to a REGISTER message will be a READY message.

  Please note that if a client driver maintains multiple connections to a
  Cassandra node and/or connections to multiple nodes, it is advised to
  dedicate a handful of connections to receive events, but to *not* register
  for events on all connections, as this would only result in receiving
  multiple times the same event messages, wasting bandwidth.


4.1.9. NEXT

  Request the next page of result if paging was requested by a QUERY or EXECUTE
  statement and there is more result to fetch (see Section 7 for more details).
  The body of a NEXT message is a single [int] indicating the number of maximum
  rows to return with the next page of results (it is equivalent to the
  <result_page_size> in a QUERY or EXECUTE message).

  The result to a NEXT message will be a RESULT message.


4.2. Responses

  This section describes the content of the frame body for the different
  responses. Please note that to make room for future evolution, clients should
  support extra informations (that they should simply discard) to the one
  described in this document at the end of the frame body.

4.2.1. ERROR

  Indicates an error processing a request. The body of the message will be an
  error code ([int]) followed by a [string] error message. Then, depending on
  the exception, more content may follow. The error codes are defined in
  Section 8, along with their additional content if any.


4.2.2. READY

  Indicates that the server is ready to process queries. This message will be
  sent by the server either after a STARTUP message if no authentication is
  required, or after a successful CREDENTIALS message.

  The body of a READY message is empty.


4.2.3. AUTHENTICATE

  Indicates that the server require authentication, and which authentication
  mechanism to use.

  The authentication is SASL based and thus consists on a number of server
  challenges (AUTH_CHALLENGE, Section 4.2.7) followed by client responses
  (AUTH_RESPONSE, Section 4.1.2). The Initial exchange is however boostrapped
  by an initial client response. The details of that exchange (including how
  much challenge-response pair are required) are specific to the authenticator
  in use. The exchange ends when the server sends an AUTH_SUCCESS message or
  an ERROR message.

  This message will be sent following a STARTUP message if authentication is
  required and must be answered by a AUTH_RESPONSE message from the client.

  The body consists of a single [string] indicating the full class name of the
  IAuthenticator in use.


4.2.4. SUPPORTED

  Indicates which startup options are supported by the server. This message
  comes as a response to an OPTIONS message.

  The body of a SUPPORTED message is a [string multimap]. This multimap gives
  for each of the supported STARTUP options, the list of supported values.


4.2.5. RESULT

  The result to a query (QUERY, PREPARE or EXECUTE messages).

  The first element of the body of a RESULT message is an [int] representing the
  `kind` of result. The rest of the body depends on the kind. The kind can be
  one of:
    0x0001    Void: for results carrying no information.
    0x0002    Rows: for results to select queries, returning a set of rows.
    0x0003    Set_keyspace: the result to a `use` query.
    0x0004    Prepared: result to a PREPARE message.
    0x0005    Schema_change: the result to a schema altering query.

  The body for each kind (after the [int] kind) is defined below.


4.2.5.1. Void

  The rest of the body for a Void result is empty. It indicates that a query was
  successful without providing more information.


4.2.5.2. Rows

  Indicates a set of rows. The rest of body of a Rows result is:
    <metadata><rows_count><rows_content>
  where:
    - <metadata> is composed of:
        <flags><columns_count><global_table_spec>?<col_spec_1>...<col_spec_n>
      where:
        - <flags> is an [int]. The bits of <flags> provides information on the
          formatting of the remaining informations. A flag is set if the bit
          corresponding to its `mask` is set. Supported flags are, given there
          mask:
            0x0001    Global_tables_spec: if set, only one table spec (keyspace
                      and table name) is provided as <global_table_spec>. If not
                      set, <global_table_spec> is not present.
            0x0002    Has_more_pages: indicates whether this is not the last
                      page of results and more should be retrieve using a NEXT
                      message. If not set, this is the laste "page" of result
                      and NEXT cannot and should not be used. If no result
                      paging has been requested in the QUERY/EXECUTE/BATCH
                      message, this will never be set.
        - <columns_count> is an [int] representing the number of columns selected
          by the query this result is of. It defines the number of <col_spec_i>
          elements in and the number of element for each row in <rows_content>.
        - <global_table_spec> is present if the Global_tables_spec is set in
          <flags>. If present, it is composed of two [string] representing the
          (unique) keyspace name and table name the columns return are of.
        - <col_spec_i> specifies the columns returned in the query. There is
          <column_count> such column specification that are composed of:
            (<ksname><tablename>)?<column_name><type>
          The initial <ksname> and <tablename> are two [string] are only present
          if the Global_tables_spec flag is not set. The <column_name> is a
          [string] and <type> is an [option] that correspond to the column name
          and type. The option for <type> is either a native type (see below),
          in which case the option has no value, or a 'custom' type, in which
          case the value is a [string] representing the full qualified class
          name of the type represented. Valid option ids are:
            0x0000    Custom: the value is a [string], see above.
            0x0001    Ascii
            0x0002    Bigint
            0x0003    Blob
            0x0004    Boolean
            0x0005    Counter
            0x0006    Decimal
            0x0007    Double
            0x0008    Float
            0x0009    Int
            0x000B    Timestamp
            0x000C    Uuid
            0x000D    Varchar
            0x000E    Varint
            0x000F    Timeuuid
            0x0010    Inet
            0x0020    List: the value is an [option], representing the type
                            of the elements of the list.
            0x0021    Map: the value is two [option], representing the types of the
                           keys and values of the map
            0x0022    Set: the value is an [option], representing the type
                            of the elements of the set
    - <rows_count> is an [int] representing the number of rows present in this
      result. Those rows are serialized in the <rows_content> part.
    - <rows_content> is composed of <row_1>...<row_m> where m is <rows_count>.
      Each <row_i> is composed of <value_1>...<value_n> where n is
      <columns_count> and where <value_j> is a [bytes] representing the value
      returned for the jth column of the ith row. In other words, <rows_content>
      is composed of (<rows_count> * <columns_count>) [bytes].


4.2.5.3. Set_keyspace

  The result to a `use` query. The body (after the kind [int]) is a single
  [string] indicating the name of the keyspace that has been set.


4.2.5.4. Prepared

  The result to a PREPARE message. The rest of the body of a Prepared result is:
    <id><metadata>
  where:
    - <id> is [short bytes] representing the prepared query ID.
    - <metadata> is defined exactly as for a Rows RESULT (See section 4.2.5.2).

  Note that prepared query ID return is global to the node on which the query
  has been prepared. It can be used on any connection to that node and this
  until the node is restarted (after which the query must be reprepared).

4.2.5.5. Schema_change

  The result to a schema altering query (creation/update/drop of a
  keyspace/table/index). The body (after the kind [int]) is composed of 3
  [string]:
    <change><keyspace><table>
  where:
    - <change> describe the type of change that has occured. It can be one of
      "CREATED", "UPDATED" or "DROPPED".
    - <keyspace> is the name of the affected keyspace or the keyspace of the
      affected table.
    - <table> is the name of the affected table. <table> will be empty (i.e.
      the empty string "") if the change was affecting a keyspace and not a
      table.

  Note that queries to create and drop an index are considered as change
  updating the table the index is on.


4.2.6. EVENT

  And event pushed by the server. A client will only receive events for the
  type it has REGISTER to. The body of an EVENT message will start by a
  [string] representing the event type. The rest of the message depends on the
  event type. The valid event types are:
    - "TOPOLOGY_CHANGE": events related to change in the cluster topology.
      Currently, events are sent when new nodes are added to the cluster, and
      when nodes are removed. The body of the message (after the event type)
      consists of a [string] and an [inet], corresponding respectively to the
      type of change ("NEW_NODE" or "REMOVED_NODE") followed by the address of
      the new/removed node.
    - "STATUS_CHANGE": events related to change of node status. Currently,
      up/down events are sent. The body of the message (after the event type)
      consists of a [string] and an [inet], corresponding respectively to the
      type of status change ("UP" or "DOWN") followed by the address of the
      concerned node.
    - "SCHEMA_CHANGE": events related to schema change. The body of the message
      (after the event type) consists of 3 [string] corresponding respectively
      to the type of schema change ("CREATED", "UPDATED" or "DROPPED"),
      followed by the name of the affected keyspace and the name of the
      affected table within that keyspace. For changes that affect a keyspace
      directly, the table name will be empty (i.e. the empty string "").

  All EVENT message have a streamId of -1 (Section 2.3).

  Please note that "NEW_NODE" and "UP" events are sent based on internal Gossip
  communication and as such may be sent a short delay before the binary
  protocol server on the newly up node is fully started. Clients are thus
  advise to wait a short time before trying to connect to the node (1 seconds
  should be enough), otherwise they may experience a connection refusal at
  first.

4.2.7. AUTH_CHALLENGE

  A server authentication challenge (see AUTH_RESPONSE (Section 4.1.2) for more
  details).

  The body of this message is a single [bytes] token. The details of what this
  token contains (and when it can be null/empty, if ever) depends on the actual
  authenticator used.

  Clients are expected to answer the server challenge by an AUTH_RESPONSE
  message.

4.2.7. AUTH_SUCCESS

  Indicate the success of the authentication phase. See Section 4.2.3 for more
  details.

  The body of this message is a single [bytes] token holding final information
  from the server that the client may require to finish the authentication
  process. What that token contains and whether it can be null depends on the
  actual authenticator used.


5. Compression

  Frame compression is supported by the protocol, but then only the frame body
  is compressed (the frame header should never be compressed).

  Before being used, client and server must agree on a compression algorithm to
  use, which is done in the STARTUP message. As a consequence, a STARTUP message
  must never be compressed.  However, once the STARTUP frame has been received
  by the server can be compressed (including the response to the STARTUP
  request). Frame do not have to be compressed however, even if compression has
  been agreed upon (a server may only compress frame above a certain size at its
  discretion). A frame body should be compressed if and only if the compressed
  flag (see Section 2.2) is set.


6. Collection types

  This section describe the serialization format for the collection types:
  list, map and set. This serialization format is both useful to decode values
  returned in RESULT messages but also to encode values for EXECUTE ones.

  The serialization formats are:
     List: a [short] n indicating the size of the list, followed by n elements.
           Each element is [short bytes] representing the serialized element
           value.
     Map: a [short] n indicating the size of the map, followed by n entries.
          Each entry is composed of two [short bytes] representing the key and
          the value of the entry map.
     Set: a [short] n indicating the size of the set, followed by n elements.
          Each element is [short bytes] representing the serialized element
          value.


7. Result paging

  The protocol allows for paging the result of queries. For that, the QUERY and
  EXECUTE messages have a <result_page_size> value that indicate the desired
  page size in CQL3 rows.

  If a positive value is provided for <result_page_size>, the result set of the
  RESULT message returned for the query will contain at most the
  <result_page_size> first rows of the query result. If that first page of result
  contains the full result set for the query, the RESULT message (of kind `Rows`)
  will have the Has_more_pages flag *not* set. However, if some results are not
  part of the first response, the Has_more_pages flag will be set. In that latter
  case, more rows of the result can be retrieved by sending a NEXT message *with the
  same stream id than the initial query*. The NEXT message also contains its own
  <result_page_size> that control how many of the remaining result rows will be
  sent in response. If the response to this NEXT message still does not contains
  the full remainder of the query result set (the Has_more_pages is set once more),
  another NEXT message can be send for more result, etc...

  If a RESULT message has the Has_more_pages flag set and any other message than
  a NEXT message is send on the same stream id, the query is cancelled and no more
  of its result can be retrieved.

  Only CQL3 queries that return a result set (RESULT message with a Rows `kind`)
  support paging. For other type of queries, the <result_page_size> value is
  ignored.

  The <result_page_size> can be set to a negative value to disable paging (in
  which case the whole result set will be retuned in the first RESULT message,
  message that will not have the Has_more_pages flag set). The
  <result_page_size> value cannot be 0.

  Note to client implementors:
  - While <result_page_size> can be as low as 1, it will likely be detrimental
    to performance to pick a value too low. A value below 100 is probably too
    low for most use cases.
  - Clients should not rely on the actual size of the result set returned to
    decide if a NEXT message should be issued. Instead, they should always
    check the Has_more_pages flag (unless they did not enabled paging for the query
    obviously). Clients should also not assert that no result will have more than
    <result_page_size> results. While the current implementation always respect
    the exact value of <result_page_size>, we reserve ourselves the right to return
    slightly smaller or bigger pages in the future for performance reasons.


8. Error codes

  The supported error codes are described below:
    0x0000    Server error: something unexpected happened. This indicates a
              server-side bug.
    0x000A    Protocol error: some client message triggered a protocol
              violation (for instance a QUERY message is sent before a STARTUP
              one has been sent)
    0x0100    Bad credentials: CREDENTIALS request failed because Cassandra
              did not accept the provided credentials.

    0x1000    Unavailable exception. The rest of the ERROR message body will be
                <cl><required><alive>
              where:
                <cl> is the [consistency] level of the query having triggered
                     the exception.
                <required> is an [int] representing the number of node that
                           should be alive to respect <cl>
                <alive> is an [int] representing the number of replica that
                        were known to be alive when the request has been
                        processed (since an unavailable exception has been
                        triggered, there will be <alive> < <required>)
    0x1001    Overloaded: the request cannot be processed because the
              coordinator node is overloaded
    0x1002    Is_bootstrapping: the request was a read request but the
              coordinator node is bootstrapping
    0x1003    Truncate_error: error during a truncation error.
    0x1100    Write_timeout: Timeout exception during a write request. The rest
              of the ERROR message body will be
                <cl><received><blockfor><writeType>
              where:
                <cl> is the [consistency] level of the query having triggered
                     the exception.
                <received> is an [int] representing the number of nodes having
                           acknowledged the request.
                <blockfor> is the number of replica whose acknowledgement is
                           required to achieve <cl>.
                <writeType> is a [string] that describe the type of the write
                            that timeouted. The value of that string can be one
                            of:
                             - "SIMPLE": the write was a non-batched
                               non-counter write.
                             - "BATCH": the write was a (logged) batch write.
                               If this type is received, it means the batch log
                               has been successfully written (otherwise a
                               "BATCH_LOG" type would have been send instead).
                             - "UNLOGGED_BATCH": the write was an unlogged
                               batch. Not batch log write has been attempted.
                             - "COUNTER": the write was a counter write
                               (batched or not).
                             - "BATCH_LOG": the timeout occured during the
                               write to the batch log when a (logged) batch
                               write was requested.
    0x1200    Read_timeout: Timeout exception during a read request. The rest
              of the ERROR message body will be
                <cl><received><blockfor><data_present>
              where:
                <cl> is the [consistency] level of the query having triggered
                     the exception.
                <received> is an [int] representing the number of nodes having
                           answered the request.
                <blockfor> is the number of replica whose response is
                           required to achieve <cl>. Please note that it is
                           possible to have <received> >= <blockfor> if
                           <data_present> is false. And also in the (unlikely)
                           case were <cl> is achieved but the coordinator node
                           timeout while waiting for read-repair
                           acknowledgement.
                <data_present> is a single byte. If its value is 0, it means
                               the replica that was asked for data has not
                               responded. Otherwise, the value is != 0.

    0x2000    Syntax_error: The submitted query has a syntax error.
    0x2100    Unauthorized: The logged user doesn't have the right to perform
              the query.
    0x2200    Invalid: The query is syntactically correct but invalid.
    0x2300    Config_error: The query is invalid because of some configuration issue
    0x2400    Already_exists: The query attempted to create a keyspace or a
              table that was already existing. The rest of the ERROR message
              body will be <ks><table> where:
                <ks> is a [string] representing either the keyspace that
                     already exists, or the keyspace in which the table that
                     already exists is.
                <table> is a [string] representing the name of the table that
                        already exists. If the query was attempting to create a
                        keyspace, <table> will be present but will be the empty
                        string.
    0x2500    Unprepared: Can be thrown while a prepared statement tries to be
              executed if the provide prepared statement ID is not known by
              this host. The rest of the ERROR message body will be [short
              bytes] representing the unknown ID.

9. Changes from v1
  * Protocol is versioned to allow old client connects to a newer server, if a
    newer client connects to an older server, it needs to check if it gets a
    ProtocolException on connection and try connecting with a lower version.
  * A query can now have bind variables even though the statement is not
    prepared; see Section 4.1.4.
  * A new BATCH message allows to batch a set of queries (prepared or not); see 
    Section 4.1.7.
  * Authentication now uses SASL. Concretely, the CREDENTIALS message has been
    removed and replaced by a server/client challenges/responses exchanges (done
    through the new AUTH_RESPONSE/AUTH_CHALLENGE messages). See Section 4.2.3 for
    details.
  * Query paging has been added (Section 7): QUERY and EXECUTE message have an
    additional <result_page_size> [int], a new NEXT message has been added and
    the Rows kind of RESULT message has an additional flag. Note that paging is
    optional, and a client that don't want to handle it can always pass -1 for
    the <result_page_size> in QUERY and EXECUTE.
