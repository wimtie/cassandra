/**
 * Autogenerated by Thrift
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 */
package org.apache.cassandra.service;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.Collections;
import java.util.BitSet;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.thrift.*;
import org.apache.thrift.meta_data.*;
import org.apache.thrift.protocol.*;

/**
 * Authentication requests can contain any data, dependent on the AuthenticationBackend used
 */
public class AuthenticationRequest implements TBase<AuthenticationRequest._Fields>, java.io.Serializable, Cloneable {
  private static final TStruct STRUCT_DESC = new TStruct("AuthenticationRequest");

  private static final TField CREDENTIALS_FIELD_DESC = new TField("credentials", TType.MAP, (short)1);

  public Map<String,String> credentials;

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements TFieldIdEnum {
    CREDENTIALS((short)1, "credentials");

    private static final Map<Integer, _Fields> byId = new HashMap<Integer, _Fields>();
    private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

    static {
      for (_Fields field : EnumSet.allOf(_Fields.class)) {
        byId.put((int)field._thriftId, field);
        byName.put(field.getFieldName(), field);
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, or null if its not found.
     */
    public static _Fields findByThriftId(int fieldId) {
      return byId.get(fieldId);
    }

    /**
     * Find the _Fields constant that matches fieldId, throwing an exception
     * if it is not found.
     */
    public static _Fields findByThriftIdOrThrow(int fieldId) {
      _Fields fields = findByThriftId(fieldId);
      if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
      return fields;
    }

    /**
     * Find the _Fields constant that matches name, or null if its not found.
     */
    public static _Fields findByName(String name) {
      return byName.get(name);
    }

    private final short _thriftId;
    private final String _fieldName;

    _Fields(short thriftId, String fieldName) {
      _thriftId = thriftId;
      _fieldName = fieldName;
    }

    public short getThriftFieldId() {
      return _thriftId;
    }

    public String getFieldName() {
      return _fieldName;
    }
  }

  // isset id assignments

  public static final Map<_Fields, FieldMetaData> metaDataMap = Collections.unmodifiableMap(new EnumMap<_Fields, FieldMetaData>(_Fields.class) {{
    put(_Fields.CREDENTIALS, new FieldMetaData("credentials", TFieldRequirementType.REQUIRED, 
        new MapMetaData(TType.MAP, 
            new FieldValueMetaData(TType.STRING), 
            new FieldValueMetaData(TType.STRING))));
  }});

  static {
    FieldMetaData.addStructMetaDataMap(AuthenticationRequest.class, metaDataMap);
  }

  public AuthenticationRequest() {
  }

  public AuthenticationRequest(
    Map<String,String> credentials)
  {
    this();
    this.credentials = credentials;
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public AuthenticationRequest(AuthenticationRequest other) {
    if (other.isSetCredentials()) {
      Map<String,String> __this__credentials = new HashMap<String,String>();
      for (Map.Entry<String, String> other_element : other.credentials.entrySet()) {

        String other_element_key = other_element.getKey();
        String other_element_value = other_element.getValue();

        String __this__credentials_copy_key = other_element_key;

        String __this__credentials_copy_value = other_element_value;

        __this__credentials.put(__this__credentials_copy_key, __this__credentials_copy_value);
      }
      this.credentials = __this__credentials;
    }
  }

  public AuthenticationRequest deepCopy() {
    return new AuthenticationRequest(this);
  }

  @Deprecated
  public AuthenticationRequest clone() {
    return new AuthenticationRequest(this);
  }

  public int getCredentialsSize() {
    return (this.credentials == null) ? 0 : this.credentials.size();
  }

  public void putToCredentials(String key, String val) {
    if (this.credentials == null) {
      this.credentials = new HashMap<String,String>();
    }
    this.credentials.put(key, val);
  }

  public Map<String,String> getCredentials() {
    return this.credentials;
  }

  public AuthenticationRequest setCredentials(Map<String,String> credentials) {
    this.credentials = credentials;
    return this;
  }

  public void unsetCredentials() {
    this.credentials = null;
  }

  /** Returns true if field credentials is set (has been asigned a value) and false otherwise */
  public boolean isSetCredentials() {
    return this.credentials != null;
  }

  public void setCredentialsIsSet(boolean value) {
    if (!value) {
      this.credentials = null;
    }
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case CREDENTIALS:
      if (value == null) {
        unsetCredentials();
      } else {
        setCredentials((Map<String,String>)value);
      }
      break;

    }
  }

  public void setFieldValue(int fieldID, Object value) {
    setFieldValue(_Fields.findByThriftIdOrThrow(fieldID), value);
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case CREDENTIALS:
      return getCredentials();

    }
    throw new IllegalStateException();
  }

  public Object getFieldValue(int fieldId) {
    return getFieldValue(_Fields.findByThriftIdOrThrow(fieldId));
  }

  /** Returns true if field corresponding to fieldID is set (has been asigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    switch (field) {
    case CREDENTIALS:
      return isSetCredentials();
    }
    throw new IllegalStateException();
  }

  public boolean isSet(int fieldID) {
    return isSet(_Fields.findByThriftIdOrThrow(fieldID));
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof AuthenticationRequest)
      return this.equals((AuthenticationRequest)that);
    return false;
  }

  public boolean equals(AuthenticationRequest that) {
    if (that == null)
      return false;

    boolean this_present_credentials = true && this.isSetCredentials();
    boolean that_present_credentials = true && that.isSetCredentials();
    if (this_present_credentials || that_present_credentials) {
      if (!(this_present_credentials && that_present_credentials))
        return false;
      if (!this.credentials.equals(that.credentials))
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  public void read(TProtocol iprot) throws TException {
    TField field;
    iprot.readStructBegin();
    while (true)
    {
      field = iprot.readFieldBegin();
      if (field.type == TType.STOP) { 
        break;
      }
      _Fields fieldId = _Fields.findByThriftId(field.id);
      if (fieldId == null) {
        TProtocolUtil.skip(iprot, field.type);
      } else {
        switch (fieldId) {
          case CREDENTIALS:
            if (field.type == TType.MAP) {
              {
                TMap _map12 = iprot.readMapBegin();
                this.credentials = new HashMap<String,String>(2*_map12.size);
                for (int _i13 = 0; _i13 < _map12.size; ++_i13)
                {
                  String _key14;
                  String _val15;
                  _key14 = iprot.readString();
                  _val15 = iprot.readString();
                  this.credentials.put(_key14, _val15);
                }
                iprot.readMapEnd();
              }
            } else { 
              TProtocolUtil.skip(iprot, field.type);
            }
            break;
        }
        iprot.readFieldEnd();
      }
    }
    iprot.readStructEnd();

    // check for required fields of primitive type, which can't be checked in the validate method
    validate();
  }

  public void write(TProtocol oprot) throws TException {
    validate();

    oprot.writeStructBegin(STRUCT_DESC);
    if (this.credentials != null) {
      oprot.writeFieldBegin(CREDENTIALS_FIELD_DESC);
      {
        oprot.writeMapBegin(new TMap(TType.STRING, TType.STRING, this.credentials.size()));
        for (Map.Entry<String, String> _iter16 : this.credentials.entrySet())
        {
          oprot.writeString(_iter16.getKey());
          oprot.writeString(_iter16.getValue());
        }
        oprot.writeMapEnd();
      }
      oprot.writeFieldEnd();
    }
    oprot.writeFieldStop();
    oprot.writeStructEnd();
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder("AuthenticationRequest(");
    boolean first = true;

    sb.append("credentials:");
    if (this.credentials == null) {
      sb.append("null");
    } else {
      sb.append(this.credentials);
    }
    first = false;
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws TException {
    // check for required fields
    if (credentials == null) {
      throw new TProtocolException("Required field 'credentials' was not present! Struct: " + toString());
    }
  }

}

