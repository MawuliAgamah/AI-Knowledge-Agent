


class KnowledgeGraphService:
    """Service for knowledge graph operations"""
    
    def __init__(self,db_client,llm_service):
        self.llm_service = llm_service
        self.db_client = db_client


    def extract_ontology(self, document_id):
        """Extract ontology from document"""
        document = self.db_client.get_document(document_id)
        print(f"\n{'='*80}")
        print(f"🔍 EXTRACTING ONTOLOGY FOR DOCUMENT: {document.title}")
        print(f"{'='*80}\n")
        
        chunks = document.textChunks
        print(f"📚 Found {len(chunks)} chunks to process\n")
        
        all_ontologies = []
        
        for i, chunk in enumerate(chunks):
            print(f"\n{'-'*80}")
            print(f"📝 CHUNK #{i+1}/{len(chunks)} (ID: {chunk.id})")
            print(f"{'-'*80}")
            
            # Print chunk content preview
            print(f"\nCONTENT:\n{chunk.content}\n")
            
            # Extract and print ontology
            print(f"ONTOLOGY EXTRACTION:")
            try:
                ontology = self.llm_service.extract_ontology(chunk)
                
                # Pretty print the ontology
                if isinstance(ontology, dict) and 'entities' in ontology and ontology['entities']:
                    entities = ontology['entities']
                    print(f"\n📊 ENTITIES ({len(entities)}):")
                    for entity in entities:
                        print(f"  • {entity['name']} ({entity['type']}/{entity['category']})")
                elif hasattr(ontology, 'entities') and ontology.entities:
                    print(f"\n📊 ENTITIES ({len(ontology.entities)}):")
                    for entity in ontology.entities:
                        print(f"  • {entity.name} ({entity.type}/{entity.category})")
                else:
                    print("\n📊 No entities found")
    
                if isinstance(ontology, dict) and 'relationships' in ontology and ontology['relationships']:
                    relationships = ontology['relationships']
                    print(f"\n🔗 RELATIONSHIPS ({len(relationships)}):")
                    for rel in relationships:
                        print(f"  • {rel['source']} → {rel['relation']} → {rel['target']}")
                        print(f"    Context: \"{rel['context']}\"")
                elif hasattr(ontology, 'relationships') and ontology.relationships:
                    print(f"\n🔗 RELATIONSHIPS ({len(ontology.relationships)}):")
                    for rel in ontology.relationships:
                        print(f"  • {rel.source} → {rel.relation} → {rel.target}")
                        print(f"    Context: \"{rel.context}\"")
                else:
                    print("\n🔗 No relationships found")
                          
                all_ontologies.append(ontology)
                
            except Exception as e:
                print(f"\n❌ ERROR: Failed to extract ontology: {str(e)}")
                print("  The LLM may have had difficulty parsing this text.")
            
            print()
            
        print(f"\n{'='*80}")
        print(f"✅ ONTOLOGY EXTRACTION COMPLETE: {len(chunks)} chunks processed")
        print(f"{'='*80}\n")
        
        return all_ontologies


    def save_document_ontology(self, document_id, ontology):
        """Save ontology to document"""
        self.db_client.save_document_ontology(document_id, ontology)

    
